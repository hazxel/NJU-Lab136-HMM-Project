function A_inf = calcPiProbability(P, method)

if nargin < 1; method = "Null"; end

A = P + eye(size(P));

switch method
  case "Eig"
    [V, D] = eig(A);
    [~, i] = max(diag(D));
    D(:) = 0;
    D((i - 1) * (size(D, 1) + 1) + 1) = 1;
    A_inf = V * D / V;
    A_inf = A_inf(:,1);
  case "Svd"
    [~, ~, V] = svd(P);
    A_inf = V(:,end);
  case "Null"
    A_inf = null(P);
end

A_inf = A_inf ./ sum(sort(A_inf));

end

