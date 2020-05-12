import subprocess

if __name__ == "__main__":

  version = "v3"

  settings = {}

  for run in [ "9883,3-140", "9885,6-140", "9886,10-140", "9911,3-170", "9910,3-200", "9909,3-240", ]: 
      settings[run] = "ABS-LH2"

  for run in ["10243,3-140", "10245,6-140", "10246,10-140", "10268,3-170", "10267,3-200", "10265,3-240", ]: 
      settings[run] = "ABS-LH2-EMPTY"

  for run in ["10314,3-140", "10317,4-140", "10318,6-140", "10319,10-140", ]:
      settings[run] = "ABS-SOLID-EMPTY"

  for run in ["10508,3-140", "10504,4-140", "10509,6-140", ]:
      settings[run] = "ABS-SOLID-LiH" 


          

  for opt, ABS in settings.iteritems():
      print "Doing "+opt+" for "+ABS
      callingstring = "./pymovedata_dojobsubmctemplate.sh "+ABS+" "+'"'+opt+'"'+" "+version
      print callingstring
      rc = subprocess.check_call(["./pymovedata_dojobsubmctemplate.sh", ABS, '"'+opt+'"', version])
