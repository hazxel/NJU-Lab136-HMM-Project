function drawEmission(folder, N, A_inf, B, B_edges, climits)

% figureName = folder + "/Emission";
figureName = [];

[~, ~, nR, nRange] = getN(N);
B = B .* A_inf';
B = reshape(B, [numel(B_edges)-1 N'+1]);

logB = (log(B) - climits(1)) ./ diff(climits);
logB = reshape(ind2rgb(im2uint8(logB(:)), jet(256)), [size(B) 3]);

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
ax = getAxes("EmissionVectorMesh", figureName);

mesh(ax, nRange{:}, squeeze(B(end,:,:)), "CData",squeeze(logB(end,:,:,:)), surfaceProperties{:});
set(ax, axesProperties{:});
saveFigure("EmissionVectorMesh", folder);


scale = 2;
imageB = ones([numel(B_edges)-1 (N'+1)*scale+2 3]);
imageB(:,2:end-1,2:end-1,:) = repelem(logB, 1, scale, scale);

axesProperties = {
  "Visible"       false
  "DataAspectRatio" [1 1 1]
}';
ax = getAxes("EmissionMatrix", figureName);

imagesc(ax, reshape(permute(imageB, [2 3 1 4]), [((N'+1)*scale+2).*[1 numel(B_edges)-1] 3]))
set(ax, axesProperties{:});
saveFigure("EmissionMatrix", folder);

saveFigure(figureName, folder + "/Emission");

if nargout == 0; clear; end

end

