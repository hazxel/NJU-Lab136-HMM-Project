function t = updated(target, source)

attributes = dirs(target);
targetDatenums = [attributes.datenum];

attributes = dirs(source);
sourceDatenums = [attributes.datenum];

t = numel(targetDatenums) == numel(target) && numel(sourceDatenums) == numel(source) && min(targetDatenums) > max(sourceDatenums);

end


function attributes = dirs(names)

attributes(numel(names)) = struct;

for i = 1:numel(names)
  attribute = dir(names(i));
  for fieldname = fieldnames(attribute)'
    attributes(i).(fieldname{:}) = [attribute.(fieldname{:})];
  end
end

end
