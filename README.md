# README

## Setup 

### Install Chocolatey and Nuget

If you haven't already, install Chocolatey. See [installation guide](https://chocolatey.org/docs/installation).
You will also need to install `Nuget` with `choco install nuget.commandline --pre` in an administrative command prompt.

### Install the Traffic Generator

# TODO - update this
Pull the code from [the repository](https://github.com/grantcurell/generatewebtraffic/releases/tag/alpha1) and unzip it into a location of your choosing.

After you have the code, open an administrative command prompt, and navigate to the unzipped directory.

Run `nuget pack` to build the Chocolatey package.
Run `choco install -y <generate_package>` to install the traffic generator.

## Usage

| Switch         | Description                                                                                                                                                                                                                                    |
|----------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| --url          | If you don't want to pass URLs via the YML file you can provide a single URL via this switch.                                                                                                                                                  |
| --yml          | A YAML file with a configuration you would like to use. Defaults to config.yml.                                                                                                                                                                |
| --dnsfrequency | The percentage of requests that should be accompanied by a DNS request. The random module is used for this so the longer the run the close to this percentage the actual send rate will be.                                                    |
| --browsers     | The number of browsers you want to deploy.                                                                                                                                                                                                     |
| --refreshrate  | How often the browsers will open new pages. This is also affected by the jitter setting.                                                                                                                                                       |
| --jitter       | Controls randomness in the refresh rate up or down. For example if your refresh rate is 20 seconds and jitter is five, the refreshes will happen in between 15 and 25 seconds at random. The default is 10 seconds. Set to 0 to remove jitter. |
| --duration     | The duration for which you want the browsers to run. Set to 0 for infinite. The default is 60.                                                                                                                                                 |
| --log-level    | Set the log level used by the program. Options are debug, info, warning, error, and critical.                                                                                                                                                  |
| --print-usage  | Show example usage.                                                                                                                                                                                                                            |

Run a basic test with a jitter of 3, refreshes every 10 seconds, and 5 concurrent browsers:

`python generatetraffic.py --refreshrate 10 --browsers 5, --jitter 3`