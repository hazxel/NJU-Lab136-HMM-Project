function [N, A, A_inf, B, B_edges, B_inf, L] = m5_trainModel(modelFolders, mitoFolders, T, N, A, B, B_edges, L)

if nargin < 1; load parameters modelFolders; end
if nargin < 2; load parameters mitoFolders; end

% modelFolders = "model2";
% mitoFolders = ["mito32" "mito37"];
iterations = 500;

for mitoFolder = mitoFolders

if nargin < 3; load(mitoFolder + "/trajectory", "T"); end

for modelFolder = modelFolders

folder = "result/" + mitoFolder + "-" + modelFolder;

tic

if nargin < 4
  if updated(folder+".mat", [mitoFolder+"/trajectory.mat" modelFolder+"/"+["parameters" "probability" "hidden"]+".mat"]) && true
    load(folder, "L");
    if ~isempty(L) && L(end) == Inf
      saveErrorModel(folder, L, iterations);
      continue
    end
    load(folder, "N", "A", "B", "B_edges");
  else
    load(modelFolder + "/parameters", "N");
    load(modelFolder + "/probability", "A");
    load(modelFolder + "/hidden", "B", "B_edges");
    L = [];
  end
end

[~, I] = sort(cellfun(@numel, T), 'descend');
T = T(I);
T = T(cellfun(@numel, T) > 25);

ntrajs = min(numel(T), 1024);
[~, I] = sort(rand(ntrajs,1));
T = T(I(1:ntrajs));

O = cell(size(T));
for i = 1:numel(T)
  [~, ~, O{i}] = histcounts(T{i}, B_edges);
end

if iterations > numel(L)

  A = A'; B = B';

  if isempty(L)
    [AA, BB] = hmmtrain(O, A, B, 'Tolerance',Inf, 'Maxiterations',1);
    if ~any(AA(:)) && ~any(BB(:))
      L = cat(1, L, Inf);
      saveErrorModel(folder, L, iterations);
      continue
    end
  end

  C = {
  %   'Tolerance'     2e-3
    'Maxiterations' iterations - numel(L)
    'Verbose'       true
  }';
  [A, B, logliks] = hmmtrain(O, A, B, C{:});
  L = cat(1, L, logliks(:));

  A = A'; B = B';

end

A_inf = HiddenMarkov.calcPiTransition(A, "Null");
B_inf = sum(B .* shiftdim(A_inf,-1), 2);

time(folder + ".trainModel")

if nargout == 0
  if ~exist("result", "dir"); mkdir result; end
  save(folder, "N", "A", "A_inf", "B", "B_edges", "B_inf", "L");
end

end % for modelFolder
end % for mitoFolder

if nargout == 0; clear; end

end


function L = saveErrorModel(folder, LL, iterations)

L = Inf;
L = L(ones(iterations, 1));
L(1:numel(LL)) = LL(:);

time(folder + ".trainModel")

if nargout == 0
  if ~exist("result", "dir"); mkdir result; end
  save(folder, "L");
end

if nargout == 0; clear; end

end
