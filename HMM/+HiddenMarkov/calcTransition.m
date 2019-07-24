function A = calcTransition(P, dt)

A = P ^ (1/dt);

A = A ./ sum(sort(A));

end

