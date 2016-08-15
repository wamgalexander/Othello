% time     5~12s   12~19s  19~26s  26~33s  33~40s  40~47s  
% cell     K~X     Y~AL    AM~AZ   BA~BN   BO~CB   CC~CP   
%          47~55s  54~61s  61~68s  68~75s
%          CQ~DD   DE~DR   DS~DF   DG~DT


function time_replace(filename, tab, count, total)
    rows = [{'5'} {'6'} {'7'} {'8'} {'9'} {'15'} {'16'} {'17'} {'18'} {'19'} {'20'} {'21'} {'22'} {'23'} {'24'} {'25'} {'26'} {'27'} {'28'} {'29'} {'30'} {'31'} {'32'} {'33'} {'34'} {'35'} {'36'} {'37'} {'38'} {'39'} {'40'} {'41'} {'42'} {'43'} {'44'} {'45'} {'46'} {'47'} {'48'} {'49'} {'50'} {'51'} {'52'} {'53'} {'54'} {'55'}];
    cols = [{'F'} {'G'} {'H'}];
    channels = [{'O1'}, {'OZ'}, {'O2'}];
    startIndex = [{'K'}, {'Y'}, {'AM'}, {'BA'}, {'BO'}, {'CC'}, {'CQ'}, {'DE'}, {'DS'}, {'DG'}];
    endIndex = [{'X'}, {'AL'}, {'AZ'}, {'BN'}, {'CB'}, {'CP'}, {'DD'}, {'DR'}, {'DF'}, {'DT'}];
    times = [{'05~12s'}, {'12~19s'}, {'19~26s'}, {'26~33s'}, {'33~40s'}, {'40~47s'}, {'47~55s'}, {'54~61s'}, {'61~68s'}, {'68~75s'}];
    
    tab = lower(tab);
    tabTotal = length(cols) *  9;
    tabCount = 0;
    
    filename = filename(1:length(filename)-4);
    
    for i = 1 : length(cols)
        for k = 2 : 10
            content = [];
            for j = 1 : length(rows) 
                item = strcat('=AVERAGE(''', upper(tab), '_', channels(i), '''!', startIndex(k), rows(j), ':', endIndex(k), rows(j), ')');
                content = [content; item];
            end
            
            outFilename = strcat(filename, '_', char(times(k)), '.xls');
            
            clc;
            fprintf('Progress : %f %%\n', (double(count)+double(tabCount)/tabTotal)/double(total) * 100);
            fprintf('Modifying %s in %s ...\n', tab, outFilename);

            location = char(strcat(cols(i), '5'));

            xlswrite(outFilename, content, tab, location);
            tabCount = tabCount + 1;

            clc;
            fprintf('Progress : %f %%\n', (double(count)+double(tabCount)/tabTotal)/double(total) * 100);
            fprintf('Modifying %s in %s ...\n', tab, outFilename);
        end
    end
    
end