import re
import os
import datetime
import napalm
import shutil
import openpyxl

Ipfilter = re.compile(r"\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}")

USERNAME = os.environ.get("USER")
PASSWORD = os.environ.get("PASS")




class GetIntfCount:
    def __init__(self):

        self.currentpath = os.getcwd()
        self.config_store_path = os.path.join(self.currentpath, "IOS_Results")
        self.source_ip_file = os.path.join(self.currentpath, "ios_device_count.txt")
        self.driver = napalm.get_network_driver("ios")
        self.today = datetime.datetime.now().date()
        self.validated_ips_list_unmatched = []
        self.validated_ips_list = []
        self.validate_source_file()


    def validate_source_file(self):

        if os.path.isfile(self.source_ip_file):
            with open(self.source_ip_file, "r") as file:
                file_get = file.read()
                ip = Ipfilter.findall(file_get)
                self.validated_ips_list_unmatched.append(ip)

            if self.validated_ips_list_unmatched == [[]]:
                print()
                print("no entry found")
                print()
            else:

                for unmatched_ip in self.validated_ips_list_unmatched[0]:
                    splitted_ip = unmatched_ip.split(".")
                    numbers = [re.sub(r'\b0+(\d)', r'\1', number) for number in splitted_ip]
                    ip_checked = ".".join(numbers)
                    self.validated_ips_list.append(ip_checked)

                if os.path.isdir(self.config_store_path):

                    print()
                    print("try to gather interface count with status 'up' from " + str(len(self.validated_ips_list)) + " devices")
                    print()
                    self.check_config_dayfolder()


                else:
                    os.mkdir(self.config_store_path)
                    print()
                    print("Storage  folder : ./IOS_Results  was created")
                    print()
                    print("try to gather interface count with status 'up' from " + str(len(self.validated_ips_list)) + " devices")
                    print()
                    self.check_config_dayfolder()



        else:
            print()
            print("No Source-File ./ios_device_count.txt found ")
            print("Creating template file: ./ios_device_count.txt ... ")
            print()

            with open(self.source_ip_file, "w") as newfile:
                val = "*** please add mangement ip's of IOS devices below; one ip per line ***"
                newfile.write(val)
            if os.path.isdir(self.config_store_path):

                print("Storage folder: ./IOS_Results")


            else:
                os.mkdir(self.config_store_path)
                print("Folder : ./IOS_Results  was created")
                print()

    def check_config_dayfolder(self):
        self.config_store_dayfolder = os.path.join(self.config_store_path, str(self.today))

        if os.path.isdir(self.config_store_dayfolder):
            self.gather_configs()


        else:
            os.mkdir(self.config_store_dayfolder)
            self.gather_configs()


    def gather_configs(self):
        header = "Hostname", "Management IP", "Interface status up"
        storage_excel = os.path.join(
            self.config_store_dayfolder, "interface_count_up" + "_.xlsx")
        wb = openpyxl.Workbook()
        sheet = wb.active
        sheet.auto_filter.ref = sheet.dimensions
        sheet.append(header)
        logfile = os.path.join(self.config_store_dayfolder, "logfile.txt")

        for ip in self.validated_ips_list:

            try:

                device = self.driver(hostname=ip,
                                     username=USERNAME,
                                     password=PASSWORD,
                                     optional_args={"port": 22})

                print("trying " + ip)
                device.open()
                hostname = device.get_facts()["hostname"]
                print("ok")
                raw_file = device.cli(["show ip int brief | inc up"])
                result_file_raw = raw_file["show ip int brief | inc up"]
                result_int_count = len(result_file_raw.split("\n"))
                line =(hostname,ip,result_int_count)
                sheet.append(line)
                with open(logfile, "a") as lgfile:
                    logline = ("{:15} :  {:30s}\n".format(ip, "ok"))
                    lgfile.write(logline)

            except:
                print("no response")
                with open(logfile, "a") as lgfile:
                    logline = ("{:15} :  {:30s}\n".format(ip, "not reachable"))
                    lgfile.write(logline)
        sheet.auto_filter.ref = sheet.dimensions
        wb.save(storage_excel)
        print("Done.")


if __name__ == "__main__":
    GetIntfCount()



