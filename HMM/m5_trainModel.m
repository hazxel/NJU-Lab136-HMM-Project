function [N, A, A_inf, B, B_edges, B_inf, L] = m5_trainModel(modelFolders, mitoFolders, T, N, A, B, B_edges, L)

if nargin < 1; load parameters modelFolders; end
if nargin < 2; load parameters mitoFolders; end

% modelFolders = "model2";
% mitoFolders = ["mito32" "mito37"];

for mitoFolder = mitoFolders

if nargin < 3; load(mitoFolder + "/trajectory", "T"); end
info = dir(mitoFolder + "/trajectory.mat");
datenum = info.datenum;

for modelFolder = modelFolders

folder = "result/" + mitoFolder + "-" + modelFolder;

if nargin < 4
  sourceDatenum = datenum;
  info = dir(modelFolder + "/parameters.mat");
  sourceDatenum = max(sourceDatenum, info.datenum);
  info = dir(modelFolder + "/probability.mat");
  sourceDatenum = max(sourceDatenum, info.datenum);
  info = dir(modelFolder + "/hidden.mat");
  sourceDatenum = max(sourceDatenum, info.datenum);

  info = dir(folder + ".mat");
  if ~isempty(info) && info.datenum > sourceDatenum && true
    load(folder, "N", "A", "B", "B_edges", "L");
  else
    load(modelFolder + "/parameters", "N");
    load(modelFolder + "/probability", "A");
    load(modelFolder + "/hidden", "B", "B_edges");
    L = [];
  end
end

tic

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

A = A'; B = B';
[AA, BB] = hmmtrain(O, A, B, 'Tolerance',Inf, 'Maxiterations',1);
if ~any(AA(:)) && ~any(BB(:))
  time(folder + ".trainModel")
  continue
end

C = {
%   'Tolerance'     2e-3
  'Maxiterations' 100
  'Verbose'       true
}';
[A, B, logliks] = hmmtrain(O, A, B, C{:});
L = cat(1, L, logliks(:));

A = A'; B = B';

A_inf = HiddenMarkov.calcPiTransition(A, "Null");
B_inf = sum(B .* shiftdim(A_inf,-1), 2);

time(folder + ".trainModel")

if nargout == 0
  if ~exist("result", "dir"); mkdir result; end
  save(folder, "N", "A", "A_inf", "B", "B_edges", "B_inf");
end

end % for modelFolder
end % for mitoFolder

if nargout == 0; clear; end

end

