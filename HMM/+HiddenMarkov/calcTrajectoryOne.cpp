
#include <algorithm>
#include <bitset>
#include <chrono>
#include <complex>
#include <functional>
#include <initializer_list>
#include <iterator>
#include <limits>
#include <memory>
#include <new>
#include <numeric>
#include <random>
#include <ratio>
#include <tuple>
#include <utility>
#include <valarray>

#include <array>
#include <deque>
#include <forward_list>
#include <list>
#include <map>
#include <queue>
#include <set>
#include <stack>
#include <unordered_map>
#include <unordered_set>
#include <vector>

#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>

#include <atomic>
#include <condition_variable>
#include <future>
#include <mutex>
#include <thread>

#include "mex.hpp"
#include "mexAdapter.hpp"

namespace std {

template <typename _Elem, typename _Traits, typename _Ty, typename _Alloc, template <typename, typename> typename _Container>
basic_ostream<_Elem, _Traits> & operator<<(basic_ostream<_Elem, _Traits> & _Ostr, _Container<_Ty, _Alloc> const & _Right) {
  _Ostr << "[";
  for (auto const & _Val : _Right) { _Ostr << " " << _Val; }
  _Ostr << " ]";
  return _Ostr;
}

} // namespace std

void throw_matlab_exception(std::string const & file, size_t line, std::string const & func, std::string const & msg) {
  std::stringstream ss;
  ss << "file " << file << " line " << line << std::endl;
  ss << func << ": " << msg;
  throw matlab::engine::MATLABException(ss.str());
}

void log_matlab_message(std::string const & file, size_t line, std::string const & func, std::string const & msg) {
  if (true) {
    std::cout << func;
    if (msg != "") std::cout << ": " << msg;
    std::cout << std::endl;
  }
}

class matlab_stream {
  using _Myt = matlab_stream;

public:
  template <typename _Ty>
  _Myt & operator<<(_Ty const & _Val) {
    if (debug) std::cout << _Val;
    return *this;
  }
  _Myt & operator<<(std::ostream &(__cdecl * _Pfn)(std::ostream &)) {
    if (debug) std::cout << _Pfn;
    return *this;
  }

  static bool debug;
} _mout;
bool matlab_stream::debug = false;

#define THROW_MATLAB(msg) throw_matlab_exception(__FILE__, __LINE__, __FUNCTION__, msg)
// #define LOG_MATLAB(msg) log_matlab_message(__FILE__, __LINE__, __FUNCTION__, msg)
#define mout (_mout << __FUNCTION__ << " ")


using namespace std;
using namespace matlab::engine;
using namespace matlab::data;
using namespace matlab::mex;

class MexFunction : public Function {
public:
  void operator()(ArgumentList outputs, ArgumentList inputs) {
    mout << boolalpha << endl;

    checkArguments(outputs, inputs);
    inputArguments(inputs);

    run();

    outputArguments(outputs);

    mout << endl;
  }

  void run_thread(size_t s_min, size_t s_max, size_t seed) {
    uniform_real_distribution<double> rd_d;
    mt19937_64 rd_g(seed);
    auto rd = bind(rd_d, rd_g);

    for (size_t t = 0; t < nsecond; ++t) {
      vector<double> dx(s_max - s_min, 0.0);
      for (size_t i = 0; i < ntimes; ++i) {
        for (size_t j = s_min; j < s_max; ++j) {
          auto r = rd();
          for (size_t k = 0; k < step; ++k) {
            if (r < F[s[j] * step + k]) {
              s[j] = FI[s[j] * step + k];
              dx[j - s_min] += vc[s[j]];
              break;
            }
          }
        }
      }
      copy(dx.begin(), dx.end(), dxs.begin() + ntrajs * t + s_min);
    }
  }

  void run() {
    mout << endl;

    size_t const run_th_num = 16;
    size_t run_th_step = (ntrajs - 1) / run_th_num + 1;
    thread run_th[run_th_num];
    for (size_t i = 0; i < run_th_num; ++i) {
      size_t s_min = min(i * run_th_step, ntrajs), s_max = min((i + 1) * run_th_step, ntrajs), seed = i;
      mout << "thread " << i << ": [" << s_min << ", " << s_max << "), seed " << seed << endl;
      run_th[i] = thread(&MexFunction::run_thread, this, s_min, s_max, seed);
    }
    for (size_t i = 0; i < run_th_num; ++i) run_th[i].join();
  }

  void checkArguments(ArgumentList outputs, ArgumentList inputs) {
    if (inputs.size() < 6) THROW_MATLAB("inputs requires: states F FI vc ntimes nsecond [debug]");
    if (outputs.size() < 1) THROW_MATLAB("outputs requires: T [s]");

    // for (size_t i = 0; i < 6; ++i) {
    //   if (inputs[i].getType() != ArrayType::DOUBLE) THROW_MATLAB("input arguments has to be double");
    // }

    if (inputs[0].getDimensions().size() != 2) THROW_MATLAB("states has to be matrix");                                              // states
    if (inputs[0].getType() != ArrayType::UINT64) THROW_MATLAB("states has to be uint64");                                           //
                                                                                                                                     //
    if (inputs[1].getDimensions().size() != 2) THROW_MATLAB("F has to be matrix");                                                   // F
    if (inputs[1].getType() != ArrayType::DOUBLE) THROW_MATLAB("F has to be double");                                                //
                                                                                                                                     //
    if (inputs[2].getDimensions().size() != 2) THROW_MATLAB("FI has to be matrix");                                                  // FI
    if (inputs[2].getType() != ArrayType::UINT64) THROW_MATLAB("FI has to be uint64");                                               //
    if (inputs[1].getDimensions() != inputs[2].getDimensions()) THROW_MATLAB("F & FI have to be the same size");                     // F & FI
                                                                                                                                     //
    if (inputs[3].getDimensions().size() != 2) THROW_MATLAB("vc has to be matrix");                                                  // vc
    if (inputs[3].getType() != ArrayType::DOUBLE) THROW_MATLAB("vc has to be double");                                               //
    if (inputs[1].getDimensions()[1] != inputs[3].getNumberOfElements()) THROW_MATLAB("col of F and number of vc have to be equal"); // F & vc
                                                                                                                                     //
    if (inputs[4].getNumberOfElements() != 1) THROW_MATLAB("ntimes has to be scalar");                                               // ntimes
    if (inputs[4].getType() != ArrayType::UINT64) THROW_MATLAB("ntimes has to be uint64");                                           //
                                                                                                                                     //
    if (inputs[5].getNumberOfElements() != 1) THROW_MATLAB("nsecond has to be scalar");                                              // nsecond
    if (inputs[5].getType() != ArrayType::UINT64) THROW_MATLAB("ntimes has to be uint64");                                           //
                                                                                                                                     //
    if (inputs.size() > 6) {                                                                                                         // debug
      if (inputs[6].getNumberOfElements() != 1) THROW_MATLAB("debug has to be scalar");                                              //
      if (inputs[6].getType() != ArrayType::LOGICAL) THROW_MATLAB("debug has to be logical");                                        //
      matlab_stream::debug = inputs[6][0];
      mout << "get dbug: " << matlab_stream::debug << endl;
    }
  }

  void inputArguments(ArgumentList inputs) {
    mout << endl;

    step = inputs[1].getDimensions()[0];
    mout << "get step: " << step << endl;

    {
      TypedArray<size_t> tmp = move(inputs[0]);
      s = move(vector<size_t>(tmp.begin(), tmp.end()));
      for (auto & s : s) --s;
      mout << "get s   : " << s.size() << endl;
    }

    {
      TypedArray<double> tmp = move(inputs[1]);
      F = move(vector<double>(tmp.begin(), tmp.end()));
      mout << "get F   : " << F.size() << endl;
    }

    {
      TypedArray<size_t> tmp = move(inputs[2]);
      FI = move(vector<size_t>(tmp.begin(), tmp.end()));
      for (auto & FI : FI) --FI;
      mout << "get FI  : " << FI.size() << endl;
    }

    {
      TypedArray<double> tmp = move(inputs[3]);
      vc = move(vector<double>(tmp.begin(), tmp.end()));
      mout << "get vc  : " << vc.size() << endl;
    }

    ntimes = inputs[4][0];
    mout << "ntimes  : " << ntimes << endl;

    ntrajs = s.size();
    nsecond = inputs[5][0];
    dxs.resize(ntrajs * nsecond);
    mout << "dxs size: " << ArrayDimensions{ ntrajs, nsecond } << endl;
    mout << "get dxs : " << dxs.size() << endl;
  }

  void outputArguments(ArgumentList outputs) {
    mout << endl;

    ArrayFactory factory;
    outputs[0] = factory.createArray({ ntrajs, nsecond }, dxs.begin(), dxs.end());
    mout << "dxs size: " << dxs.size() << endl;
    mout << "set dxs : " << ArrayDimensions{ ntrajs, nsecond } << endl;
  }

private:
  // TypedArray<double> F, FI, vc;
  vector<size_t> s;
  vector<double> F;
  vector<size_t> FI;
  vector<double> vc;
  size_t ntrajs, ntimes, nsecond;

  vector<double> dxs;
  size_t step;

  vector<double> rs;
};
