function saveFigure(figureName, filename)

if isempty(figureName); return; end

f = findall(0, "Name",figureName);
if isempty(f); return; end

if exist(filename, "dir")
  print(f, "-r0", filename + "/" + figureName, "-dpng");
else
  print(f, "-r0", filename, "-dpng");
end

end

