function [dim, n, nR, nRange] = getN(N)
% N -> dim, nR, n.

dim = size(N(:),1);
nR = cell(dim,1);
for d = 1:dim
  nR{d} = 0:N(d);
end

n = cell(dim,1);
[n{:}] = ndgrid(nR{:});
n = cat(3, n{:});

nRange = flip(nR);

end

