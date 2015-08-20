   
turbfile='/home/ccchart/wrkdir/SVN/20130808_tidal_turbines/examples/01_standard/turbines.ini'
#turbfile='turbines.ini'

turb_data={}

nturb=0
with open(turbfile) as fin:
    linein = fin.readline()
    while True:
        if linein == '':
            break
        elif linein[1:23].lower() == 'turbinefileinformation':
            linein = fin.readline()
            lsplit = linein.split('=')
            var = lsplit[0].strip()
            info = lsplit[1].strip()
            turb_data[var] = info

            linein = fin.readline()
        elif linein[1:8].lower() == 'general':
            linein = fin.readline()
            lsplit = linein.split('=')
            var = lsplit[0].strip()
            info = lsplit[1].strip()
            turb_data[var] = info

            linein = fin.readline()
        elif linein[1:8].lower() == 'turbine':
            nturb+=1
            turbTag = 'Turbine{:0>3d}'.format(nturb)
            temp={}
            while True:
                linein = fin.readline()
                if linein == '' or linein[0] == '[' :  # read end of turbine info
                    turb_data[turbTag] = temp
                    break
                if linein.strip()=='':   #blank line
                    continue
                lsplit = linein.split('=')
                var = lsplit[0].strip()
                info = lsplit[1].strip()
                temp[var] = info

print turb_data
