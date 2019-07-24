function drawDistribution(folder, N, A_inf, B_inf, B_edges, climits)

% figureName = folder + "/Distribution";
figureName = [];

[~, ~, nR, nRange] = getN(N);

if ~isempty(A_inf)

A_inf = reshape(A_inf, N(:)'+1);
C_inf = (log(A_inf) - climits(1)) ./ diff(climits);
C_inf = ind2rgb(im2uint8(C_inf), jet(256));

surfaceProperties = {
  "FaceColor"     "interp"
  "FaceAlpha"     1
  "EdgeColor"     "interp"
}';
axesProperties = {
  "YLim"          [0 N(1)]
  "XLim"          [0 N(2)]
  "ZLim"          [0 0.2]
  "YTick"         nR{1}
  "XTick"         nR{2}
  "YDir"          "reverse"
  "View"          [52.5 30]
  "YGrid"         "off"
  "XGrid"         "off"
  "FontName"      "Arial"
  "FontSize"      8
  "FontWeight"    "bold"
  "LineWidth"     1
}';
ax = getAxes("TransitionDistribution", figureName);

mesh(ax, nRange{:}, A_inf, "CData",C_inf, surfaceProperties{:});
set(ax, axesProperties{:});
saveFigure("TransitionDistribution", folder);

end

if ~isempty(B_inf)

histogramProperties = {
}';
axesProperties = {
  "XLim"          [-1.6 1.6]
  "YLim"          [0 1]
  "XTick"         B_edges
  "XTickLabelRotation" 90
  "YGrid"         "on"
  "FontName"      "Arial"
  "FontSize"      8
  "FontWeight"    "bold"
  "LineWidth"     1
}';
ax = getAxes("EmissionDistribution", figureName);

histogram(ax, "BinEdges",B_edges,"BinCounts",B_inf, histogramProperties{:});
set(ax, axesProperties{:});
saveFigure("EmissionDistribution", folder);

end

saveFigure(figureName, folder + "/Distribution");

if nargout == 0; clear; end

end

