%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% This script should be used with second_replace.m file. It will change  %
% the time interval (i.e. change '=AVERAGE(K5,X5)' to '=AVERAGE(Y5,AL5)' %
% of original .xls file.                                                 %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% time     5~12s   12~19s  19~26s  26~33s  33~40s  40~47s  
%          47~55s  54~61s  61~68s  68~75s
clear all;
t0 = clock;

total = 0;
count = 0;
times = [{'05~12s'}, {'12~19s'}, {'19~26s'}, {'26~33s'}, {'33~40s'}, {'40~47s'}, {'47~55s'}, {'54~61s'}, {'61~68s'}, {'68~75s'}];

listing = dir('.');

fPath = 'post';
if isequal(exist(fPath, 'dir'),7) % 7 = directory.
    error('post directory existed!');
end

mkdir('post');

for i = 1 : length(listing)
    if ~isempty(strfind(listing(i).name, '.cnt'))
        total = total + 1;
    end
end

disp('Preparing file...');

for i = 1 : length(listing)
    filename = listing(i).name;
    if ~isempty(strfind(listing(i).name, '.xls'))
        if ~strcmp(filename, 'template.xls')
            for j = 1 : length(times)
                copyfile(filename, strcat('./post/', filename(1:length(filename)-4), '_', char(times(j)), '.xls'));
            end
        end
    end
end

for i = 1 : length(listing)
    if ~isempty(strfind(listing(i).name, '.cnt'))
        str = listing(i).name;

        expression = '[0-9]+[Hh][Zz]';
        [startIndex, endIndex] = regexp(str, expression);

        tab = strcat(str(startIndex:endIndex-2), 'Hz');
        if endIndex + 4 == length(str)
            filename = strcat('./post/', str(1:startIndex-1), '.xls');
        else
            filename = strcat('./post/', str(1:startIndex-1), str(endIndex+2:length(str)-4), '.xls');
        end
        
        time_replace(filename, tab, count, total);
        count = count + 1;

    end
end

elapsedTime = etime(clock, t0);
fprintf('Elapsed time: %fs\n', elapsedTime);

clear all;
