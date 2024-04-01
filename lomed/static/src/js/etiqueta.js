                        var selected_device;
                        var devices = [];
                        function setup()
                        {
                            BrowserPrint.getDefaultDevice('printer', function(device)
                                    {
                                        selected_device = device;
                                        devices.push(device);
                                        
                                    }, function(error){
                                    });
                        }

                        function getConfig(){
                            BrowserPrint.getApplicationConfiguration(function(config){
                                alert(JSON.stringify(config))
                            }, function(error){
                                alert(JSON.stringify(new BrowserPrint.ApplicationConfiguration()));
                            })
                        }

                        function writeToSelectedPrinter(dataToWrite)
                        {
                        try {
                                selected_device.send(dataToWrite, undefined, errorCallback);
                        } catch (error) {
                        }

                        }

                        var readCallback = function(readData) {
                            if(readData === undefined || readData === null || readData === '')
                            {
                                
                            }
                            else
                            {
                                
                            }
                            
                        }
                        
                        var errorCallback = function(errorMessage){
                            
                        }
                        
                        function readFromSelectedPrinter()
                        {

                            selected_device.read(readCallback, errorCallback);
                            
                        }
                        
                        function getDeviceCallback(deviceList)
                        {
                            
                        }
                        $(document).ready(function() {
                            setup();
                        });

