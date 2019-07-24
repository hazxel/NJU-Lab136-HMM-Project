function x = calcSimulation(P, v, nframes, ntrajs)

[F, FI] = sortProbability(P);

x = zeros(ntrajs, numel(v));

for i = 1:numel(v)
  states = i;
  states = states(ones(ntrajs,1));
  x(:,i) = HiddenMarkov.calcTrajectoryOne(uint64(states), F, uint64(FI), v, uint64(nframes), uint64(1));
end

end

