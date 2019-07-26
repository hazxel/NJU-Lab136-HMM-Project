function drawHiddenMarkov(modelFolders, mitoFolders, N, A, A_inf, B, B_edges, B_inf, L)

if nargin < 1; load parameters modelFolders; end
if nargin < 2; load parameters mitoFolders; end

% mitoFolders = ["mito37"];
% modelFolders = "simulate";

for mitoFolder = mitoFolders
for modelFolder = modelFolders

folder = "result/" + mitoFolder + "-" + modelFolder;

if nargin < 2
  if ~exist(folder, "dir"); mkdir(folder); end
  load(folder, "N", "A", "A_inf", "B", "B_edges", "B_inf", "L");
  if L(1) == Inf; continue; end
end

tic

climits = [-30 0];
colorbarProperties = {
  "Position"      [0.1 0.1 0.7 0.8]
  "AxisLocation"  "in"
  "FontName"      "Arial"
  "FontSize"      10
  "FontWeight"    "bold"
  "LineWidth"     1
}';
axesProperties = {
  "Visible"       false
  "CLim"          climits
  "Colormap"      jet(256)
}';
ax = getAxes("Colormap");

colorbar(ax, colorbarProperties{:});
set(ax, axesProperties{:});

HiddenMarkov.drawTransition(folder, N, A, A_inf, climits);
HiddenMarkov.drawEmission(folder, N, A_inf, B, B_edges, climits);
HiddenMarkov.drawDistribution(folder, N, A_inf, B_inf, B_edges, climits);

time(folder + ".drawHiddenMarkov")

end % for modelFolder
end % for mitoFolder

end

