% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% %
% %     
% %
% %
% %
% %
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

close all;

total = 0;
count = 0;
listing = dir('.');

for i = 1 : length(listing)
    if ~isempty(strfind(listing(i).name, '.cnt'))
        total = total + 1;
        str = listing(i).name;

        expression = '[0-9]+[Hh][Zz]';
        [startIndex, endIndex] = regexp(str, expression);

        tab = strcat(str(startIndex:endIndex-2), 'Hz');
        if endIndex + 4 == length(str)
            filename = strcat(str(1:startIndex-1), '.xls');
        else
            filename = strcat(str(1:startIndex-1), str(endIndex+2:length(str)-4), '.xls');
        end
        copyfile('template.xls', filename);
    end
end

for i = 1 : length(listing)
    if ~isempty(strfind(listing(i).name, '.cnt'))
        str = listing(i).name;
        
        expression = '[0-9]+[Hh][Zz]';
        [startIndex, endIndex] = regexp(str, expression);
        
        tab = strcat(str(startIndex:endIndex-2), 'Hz');
        if endIndex + 4 == length(str)
            filename = strcat(str(1:startIndex-1), '.xls');
        else
            filename = strcat(str(1:startIndex-1), str(endIndex+2:length(str)-4), '.xls');
        end
        
        [ALLEEG EEG CURRENTSET ALLCOM] = eeglab;
        EEG = pop_loadcnt(str , 'dataformat', 'auto', 'memmapfile', '');
        [ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, 0,'gui','off'); 
        EEG = eeg_checkset( EEG );
        EEG = pop_select( EEG,'channel',{'O1' 'OZ' 'O2'});
        [ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, 1,'gui','off'); 
        EEG = pop_eegfiltnew(EEG, 5, 55, 1650, 0, [], 1);
        [ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, 2,'gui','off'); 
        eeglab redraw;
        close all;
        

        data = EEG.data;
        fs = 1000;            % sample rate
        data = double(data);  % 轉型態

        subplot(2, 2, 1);
        [Sx1,F,T, ps1] = spectrogram(data(1,:),1000,500,1000,fs); %Sx - power, F - 頻帶, T-時間
        Sx1 = abs(Sx1);

        subplot(2, 2, 2);
        [Sx2,F,T, ps2] = spectrogram(data(2,:),1000,500,1000,fs); %Sx - power, F - 頻帶, T-時間
        Sx2 = abs(Sx2);

        subplot(2, 2, 3);
        [Sx3,F,T, ps3] = spectrogram(data(3,:),1000,500,1000,fs); %Sx - power, F - 頻帶, T-時間
        Sx3 = abs(Sx3);

        close all;
        O1 = ps1; OZ = ps2; O2 = ps3;    % psd
        %O1 = Sx1; OZ = Sx2; O2 = Sx3;     % freq
        
        clc;
     
        fprintf('Progress : %f %%\n', double(count)/double(total) * 100);
        fprintf('Writing %s into %s ...\n', tab, filename);
        warning('off','MATLAB:xlswrite:AddSheet');
        xlswrite(filename, O1, strcat(tab, '_O1'), 'A1');
        fprintf('\t\t O1 done.\n');
        clc;
        fprintf('Progress : %f %%\n', (double(count) + 1/3)/double(total) * 100);
        fprintf('Writing %s into %s ...\n', tab, filename);
        fprintf('\t\t O1 done.\n');
        xlswrite(filename, OZ, strcat(tab, '_OZ'), 'A1');
        fprintf('\t\t OZ done.\n');
        clc;
        fprintf('Progress : %f %%\n', (double(count) + 2/3)/double(total) * 100);
        fprintf('Writing %s into %s ...\n', tab, filename);
        fprintf('\t\t O1 done.\n');
        fprintf('\t\t OZ done.\n');
        xlswrite(filename, O2, strcat(tab, '_O2'), 'A1');
        fprintf('\t\t O2 done.\n');
        clc;
        fprintf('Progress : %f %%\n', (double(count) + 3/3)/double(total) * 100);
        fprintf('Writing %s into %s ...\n', tab, filename);
        fprintf('\t\t O1 done.\n');
        fprintf('\t\t OZ done.\n');
        fprintf('\t\t O2 done.\n');
        count = count + 1;
        
        % Get information returned by XLSINFO on the workbook
        XL_file = [pwd '\' filename];
        [type, sheet_names] = xlsfinfo(XL_file);
        % First open Excel as a COM Automation server
        Excel = actxserver('Excel.Application');
        % Make the application invisible
        set(Excel, 'Visible', 0);
        % Make excel not display alerts
        set(Excel,'DisplayAlerts',0);
        % Get a handle to Excel's Workbooks
        Workbooks = Excel.Workbooks; 
        % Open an Excel Workbook and activate it
        Workbook=Workbooks.Open(XL_file);
        % Get the sheets in the active Workbook
        Sheets = Excel.ActiveWorkBook.Sheets;
        Workbook.Worksheets.Item(strcat(tab, '_O1')).Visible = false;
        Workbook.Worksheets.Item(strcat(tab, '_OZ')).Visible = false;
        Workbook.Worksheets.Item(strcat(tab, '_O2')).Visible = false;
        % Now save the workbook
        Workbook.Save;
        % Close the workbook
        Workbooks.Close;

    end
end

clear all;




