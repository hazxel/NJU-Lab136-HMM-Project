function drawTransition(folder, N, A, A_inf, climits)

% figureName = folder + "/Transition";
figureName = [];

[~, ~, nR, nRange] = getN(N);
A = A .* shiftdim(A_inf,-1);
A = reshape(A, [N; N]'+1);

logA = (log(A) - climits(1)) ./ diff(climits);
logA = reshape(ind2rgb(im2uint8(logA(:)), jet(256)), [size(A) 3]);

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
ax = getAxes("TransitionVectorMesh", figureName);

mesh(ax, nRange{:}, squeeze(A(:,:,1,N(2)+1)), "CData",squeeze(logA(:,:,1,N(2)+1,:)), surfaceProperties{:});
set(ax, axesProperties{:});
saveFigure("TransitionVectorMesh", folder);


axesProperties = {
  "Visible"       false
  "PlotBoxAspectRatio" [1 1 1]
}';
ax = getAxes("TransitionMatrix", figureName);

scale = 2;
imageA = ones([(N'+1)*scale+2 N'+1 3]);
imageA(2:end-1,2:end-1,:,:,:) = repelem(logA, scale, scale);
imagesc(ax, reshape(permute(imageA, [1 3 2 4 5]), [(N'+1).*((N'+1)*scale + 2) 3]));
set(ax, axesProperties{:});
saveFigure("TransitionMatrix", folder);


axesProperties = {
  "Visible"       false
  "PlotBoxAspectRatio" [1 1 1]
}';
ax = getAxes("TransitionVector", figureName);

imagesc(ax, squeeze(logA(:,:,1,N(2)+1,:)));
set(ax, axesProperties{:});
saveFigure("TransitionVector", folder);

saveFigure(figureName, folder + "/Transition");

if nargout == 0; clear; end

end

