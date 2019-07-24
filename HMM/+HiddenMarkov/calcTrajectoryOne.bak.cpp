
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

#define THROW_MATLAB(msg) throw_matlab_exception(__FILE__, __LINE__, __FUNCTION__, msg)
// #define LOG_MATLAB(msg) log_matlab_message(__FILE__, __LINE__, __FUNCTION__, msg)
#if 1
#define mout (std::cout << __FUNCTION__ << " ")
#else
class nstream {
  using _Myt = nstream;

public:
  template <typename _Ty>
  _Myt & operator<<(_Ty const & _Val) { return *this; }
  _Myt & operator<<(std::ostream &(__cdecl * _Pfn)(std::ostream &)) { return *this; }
} nout;

#define mout nout
#endif

using namespace std;
using namespace matlab::engine;
using namespace matlab::data;
using namespace matlab::mex;

class MexFunction : public Function {
public:
  void operator()(ArgumentList outputs, ArgumentList inputs) {
    cout << boolalpha << endl;

    checkArguments(outputs, inputs);
    inputArguments(inputs);

    run();

    outputArguments(outputs);

    cout << endl;
  }

  void run_thread(size_t s_min, size_t s_max, size_t seed) {
    uniform_real_distribution<double> rd_d;
    mt19937_64 rd_g(seed);
    auto rd = bind(rd_d, rd_g);

    vector<double> dx(s_max - s_min, 0.0);
    for (size_t i = 0; i < ntimes; ++i) {
      for (size_t j = s_min; j < s_max; ++j) {
        auto r = rd();
        for (size_t k = 0; k < step; ++k) {
          if (r < F[s[j] * step + k]) {
            s[j] = FI[s[j] * step + k];
            dxs[j] += vc[s[j]];
            break;
          }
        }
      }
    }
  }

  void run() {
    mout << endl;

    size_t const run_th_num = 16;
    size_t run_th_step = (ntrajs - 1) / run_th_num + 1;
    thread run_th[run_th_num];
    for (size_t i = 0; i < run_th_num; ++i) {
      mout << "thread: " << i << " " << endl;
      run_th[i] = thread(&MexFunction::run_thread, this, i * run_th_step, min((i + 1) * run_th_step, ntrajs), i);
    }
    for (size_t i = 0; i < run_th_num; ++i) run_th[i].join();
  }

  void checkArguments(ArgumentList outputs, ArgumentList inputs) {
    if (inputs.size() != 6) THROW_MATLAB("inputs requires 6 arguments");
    if (outputs.size() != 1) THROW_MATLAB("outputs requires 1 arguments");

    for (auto & input : inputs) {
      if (input.getType() != ArrayType::DOUBLE) THROW_MATLAB("input arguments has to be double");
    }

    if (inputs[0].getDimensions().size() != 2) THROW_MATLAB("1st arguments has to be matrix");                                                            // F
    if (inputs[1].getDimensions().size() != 2) THROW_MATLAB("2nd arguments has to be matrix");                                                            // FI
    if (inputs[0].getDimensions() != inputs[1].getDimensions()) THROW_MATLAB("1st & 2nd arguments have to be the same size");                             // F & FI
    if (inputs[0].getDimensions()[1] != inputs[2].getNumberOfElements()) THROW_MATLAB("col of 1st argument and number of 3rd argument have to be equal"); // F & vc
    if (inputs[3].getDimensions().size() != 2) THROW_MATLAB("4th arguments has to be matrix");                                                            // i
    if (inputs[4].getNumberOfElements() != 1) THROW_MATLAB("5th argument has to be scalar");                                                              // ntrajs
    if (inputs[5].getNumberOfElements() != 1) THROW_MATLAB("6th argument has to be scalar");                                                              // ntimes
  }

  void inputArguments(ArgumentList inputs) {
    mout << endl;

    step = inputs[0].getDimensions()[0];
    mout << "get step: " << step << endl;

    TypedArray<double> tmp = move(inputs[0]);
    F = move(vector<double>(tmp.begin(), tmp.end()));
    mout << "get F   : " << F.size() << endl;

    tmp = move(inputs[1]);
    FI = move(vector<size_t>(tmp.begin(), tmp.end()));
    for (auto & FI : FI) --FI;
    mout << "get FI  : " << FI.size() << endl;

    tmp = move(inputs[2]);
    vc = move(vector<double>(tmp.begin(), tmp.end()));
    mout << "get vc  : " << vc.size() << endl;

    ntrajs = inputs[4][0];
    ntimes = inputs[5][0];

    s = move(vector<size_t>(ntrajs, size_t(inputs[3][0]) - 1));
    mout << "get s   : " << s.size() << endl;

    dxs = move(vector<double>(ntrajs, 0.0));
    mout << "get dxs : " << dxs.size() << endl;
  }

  void outputArguments(ArgumentList outputs) {
    mout << endl;

    mout << "ntrajs: " << ntrajs << endl;
    mout << "dxs size: " << dxs.size() << endl;

    ArrayFactory factory;
    outputs[0] = factory.createArray({ ntrajs, 1 }, dxs.begin(), dxs.end());
    mout << "set dxs : " << ArrayDimensions{ ntrajs, 1 } << endl;
  }

private:
  vector<double> F;
  vector<size_t> FI;
  vector<double> vc;
  size_t ntrajs, ntimes;

  vector<size_t> s;
  vector<double> dxs;
  size_t step;

  vector<double> rs;
};
