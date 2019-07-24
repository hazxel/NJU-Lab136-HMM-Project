function A_inf = calcPiTransition(A, method)

if nargin < 1; method = "null"; end

P = A - eye(size(A));

switch method
  case "Eig"
    [V, D] = eig(A);
    [~, i] = max(diag(D));
    D(:) = 0;
    D((i - 1) * (size(D, 1) + 1) + 1) = 1;
    A_inf = V * D / V;
    A_inf = A_inf(:,1);
  case "Svd"
    if isnan(P)
      P = 0;
    end
    [~, ~, V] = svd(P);
    A_inf = V(:,end);
  case "Null"
    A_inf = null(P);
end

A_inf = A_inf ./ sum(sort(A_inf));

end

