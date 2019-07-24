function time(str, timerVal)

persistent isdisp
if isempty(isdisp); isdisp = true; end

if nargin < 1
  isdisp = ~isdisp;
  return
end

if islogical(str)
  isdisp = str(1);
  return
end

if nargin < 2
  t = toc;
else
  t = toc(timerVal);
end

if (isdisp)
  disp(join(stralign(split(str, "."), [20;25]), ".") + ": " + extractBefore(string(t)+"0000000", 7) + "s");
end

end


function str = stralign(str, length)

length(end+1:numel(str)) = 0;

for i = 1:numel(str)
  s = str(i);
  s = extractBefore(s + char(' '+zeros(1,length(i)-strlength(s))), length(i)+1);
  str(i) = s;
end

end

