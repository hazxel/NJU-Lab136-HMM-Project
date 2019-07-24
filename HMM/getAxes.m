function ax = getAxes(axesName, figureName)

if nargin < 2 || isempty(figureName)
  figureName = axesName;
end

f = findall(0, "Name",figureName);
if isempty(f)
  f = figure("Name",figureName);
end

if isempty(f.UserData)
  f.UserData.axes = struct;
end

% if ~isfield(f.UserData.axes, axesName)
%   f.UserData.axes.(axesName) = axes(f);
% end
if isfield(f.UserData.axes, axesName)
  delete(f.UserData.axes.(axesName));
end
f.UserData.axes.(axesName) = axes(f);

ax = f.UserData.axes.(axesName);

end

