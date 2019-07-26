function [B, B_edges, B_inf] = m3_calcHiddenMarkov(modelFolders, v0, A_inf, x)
% P, vc -> A, B

if nargin < 1; load parameters modelFolders; end

for folder = modelFolders

if nargin < 2
  load(folder + "/parameters", "v0", "ts");
  load(folder + "/probability", "A_inf");
  load(folder + "/hidden", "x");
end

tic

% [B, B_edges] = calcHiddenMarkov(folder, x, v0);

B_edges = calcEdgesB(folder, -v0(end)*ts, v0(1)*ts, 10); % -v0(end):0.02:v0(1);
B_edges([1 end]) = [-Inf Inf];

B = cntEmission(x, B_edges);

B_inf = sum(B .* shiftdim(A_inf,-1), 2);

time(folder + ".calcHiddenMarkov")

if nargout == 0
  save(folder + "/hidden", "B", "B_edges", "B_inf", "-append");
end

end % for folder

if nargout == 0
  clear
end

end


function B_edges = calcEdgesB(modelFolder, minedge, maxedge, nbins)

switch modelFolder
  case "model1"
    k = exp(1);
    edges = minedge*k:(maxedge-minedge)*k/nbins:maxedge*k;
    edges = (exp(edges) - exp(-edges)) / 2;
    edges = edges - min(edges);
    edges = edges ./ max(edges);
    edges = edges .* (maxedge-minedge) + minedge;
  case {"model2", "simulate"}
    k = exp(3);
    edges = minedge*k:(maxedge-minedge)*k/nbins:maxedge*k;
    edges = log(edges + sqrt(edges .^ 2 + 1));
    edges = edges - min(edges);
    edges = edges ./ max(edges);
    edges = edges .* (maxedge-minedge) + minedge;
  case "model3"
    k = exp(1);
    edges = minedge*k:(maxedge-minedge)*k/nbins:maxedge*k;
    edges = (exp(edges) - exp(-edges)) / 2;
    edges = edges - min(edges);
    edges = edges ./ max(edges);
    edges = edges .* (maxedge-minedge) + minedge;
  otherwise
    edges = minedge:(maxedge-minedge)/nbins:maxedge;
end

B_edges = edges;
% B_edges = minedge:(maxedge-minedge)/100:maxedge;
% B_edges = minedge:(maxedge-minedge)/nbins:maxedge;

end


function B = cntEmission(x, B_edges)

[ntrajs, nstates] = size(x);
B = zeros(numel(B_edges)-1, nstates);

for i = 1:nstates
  B(:,i) = histcounts(x(:,i), B_edges) ./ ntrajs;
end

end

