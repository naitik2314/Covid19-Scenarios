<h1 id="covid19_scenarios" align="center">
  COVID-19 Scenarios
</h1>

<blockquote align="center">
Models of COVID-19 outbreak trajectories and hospital demand
</blockquote>

<p align="center">
  <a href="https://covid19-scenarios.org/">
    🌐 covid19-scenarios.org
  </a>
</p>

<p align="center">
  <a href="https://covid19-scenarios.org/">
    <img
      width="100%"
      height="auto"
      src="https://user-images.githubusercontent.com/9403403/78839853-9c0aea00-79f9-11ea-92c9-593e05fd1570.gif"
      alt="An animated screenshot of the application, showcasing the user interface on main page"
    />
  </a>
</p>



<h2 id="overview" align="center">
👀 Overview
</h2>

This tool is based on the SIR model (see about page for details) that simulates a COVID19 outbreak. The population is
initially mostly susceptible (other than for initial cases). Individuals that recover from COVID19 are subsequently
immune. Currently, the parameters of the model are _not_ fit to data but are simply defaults. These might fit better for
some localities than others. In particular the initial cases counts are often only rough estimates.

The primary purpose of the tool is to explore the dynamics of COVID19 cases and the associated strain on the health care
system in the near future. The outbreak is influenced by infection control measures such as school closures, lock-down
etc. The effect of such measures can be included in the simulation by adjusting the mitigation parameters. Analogously,
you can explore the effect of isolation on specific age groups in the column "Isolated" in the table on severity
assumptions and age specific isolation.

Most parameters can be adjusted in the tool and for many of them we provide presets (scenarios).

Input data for the tool and the basic parameters of the populations are collected in the
[`/data` directory](https://github.com/neherlab/covid19_scenarios/tree/master/data). Please add data on populations and
parsers of publicly available case count data there.

<h1 align="center" />

<h2 id="users_guide" align="center">
📕 User's Guide 
</h2>

The online application provides a friendly user interface with drop downs to choose model parameters, run the model, and
export results in CSV format. A detailed process is below.

### Parameters: population

Select the population drop down and select a country/region to auto-populate the model's parameters with respective UN
population data. These parameters can be individually updated manually if necessary.

### Parameters: epidemiology

The epidemiology parameters are a combination of speed and region - specifying growth rate, seasonal variation, and
duration of hospital stay. To choose a preset distribution, select one of the options from the epidemiology drop down to
auto-populate the model's parameters with the selected parameters.

### Parameters: mitigation

Mitigation parameters represent the reduction of transmission through mitigation (infection control) measures over time.
To select a preset, click on the mitigation dropdown and select one of the options. Otherwise, the points on the graph
can be dragged and moved with the mouse. The parameter ranges from one (no infection control) to zero (complete
prevention of all transmission).

### Running the Model

Once the correct parameters are inputted, select the run button located in the Results section of the application. The
model output will be displayed in 2 graphs: Cases through time and Distribution across groups and 2 tables: Populations
and Totals/Peak.

### Exporting Results

The model's results can be exported in CSV format by clicking the "export" button in the right hand corner.

<h1 align="center" />

<h2 id="developers_guide" align="center">
🖥️ Developer's guide
</h2>

### Quick Start

#### Run natively

Install the requirements:

- git >= 2.0
- node.js >= 10 (we recommend installation through [nvm](https://github.com/nvm-sh/nvm) or
  [nvm-windows](https://github.com/coreybutler/nvm-windows))
- 1.0 < yarn < 2.0

Then in your terminal type:

```bash
git clone --recursive https://github.com/neherlab/covid19_scenarios
cd covid19_scenarios/
cp .env.example .env
yarn install
yarn dev

```

(on Windows, substitute `cp` with `copy`)

This will trigger the development server and build process. Wait for the build to finish, then navigate to
`http://localhost:3000` in a browser (last 5 versions of Chrome or Firefox are supported in development mode).

> ℹ️ Hint: type "rs<Enter>" in terminal to restart the build

> ℹ️ Hit Ctrl+C in to shutdown the server

#### Run in docker container

Install the requirements:

- Docker > 19.0
- docker-compose >= 1.25

Run docker-compose with `docker/docker-compose.dev.yml` file:

```
UID=$(id -u) docker-compose -f docker/docker-compose.dev.yml up --build

```

Variable `UID` should be set to your Unix user ID. On single-user setups these are usually 1000 on Linux and 523 on Mac.

### Directory Structure

As a developer you are most likely interested in the actual source code in `src/` directory.

| File or directory      | Contents                                      |
| ---------------------- | --------------------------------------------- |
| 📁algorithims/         | Algorithm's implementation                    |
| ├📄model.ts/           | Model's implementation                        |
| ├📄run.ts/             | Algorithm's entry point                       |
| 📁assets/              | Input data, images, and text assets           |
| 📁components/          | React components                              |
| ├📁Form/               | Form components                               |
| ├📁Main/               | Simulator's UI main component implementation  |
| &#124; ├📁Containment/ | Containment widget                            |
| &#124; ├📁Results/     | Results panel                                 |
| &#124; ├📁Scenario/    | Scenario panel                                |
| &#124; ├📁state/       | Main component's state management (hooks)     |
| &#124; ├📁validation/  | Form validation                               |
| &#124; ├📄Main.scss/   |                                               |
| &#124; ├📄Main.tsx/    | Simulator's UI main component entry point     |
| ├📄App.tsx/            | App main component                            |
| 📁locales/             | Locales for translation                       |
| 📁pages/               | Application's pages                           |
| 📁server/              | Server that serves production build artifacts |
| 📁state/               | App state management (Redux and sagas)        |
| 📁styles/              | Stylesheets                                   |
| 📁types/               | Typescript typings                            |
| 📄index.ejs            | HTML template                                 |
| 📄index.polyfilled.ts  | Entry point wrapper with polyfills            |
| 📄index.tsx            | Real entry point                              |
| 📄links.ts             | Navbar links                                  |
| 📄routes.ts            | Routes (URL-to-page mapping)                  |

### Production build

In order to replicate the production build locally, use this command:

```bash

yarn prod:watch

```

This should build the application in production mode and to start static server that will serve the app on
`http://localhost:8080` (by default)


### Translations

The translation JSON files are in [src/i18n/resources](https://github.com/neherlab/covid19_scenarios/tree/master/src/i18n/resources)
You can edit them directly or using GitLocalize. Here are the direct links to GitLocalize for each language that has translations currently:

 - [:saudi_arabia: ar](https://gitlocalize.com/repo/4360/ar/src/i18n/resources/en/common.json)
 - [:de: de](https://gitlocalize.com/repo/4360/de/src/i18n/resources/en/common.json)
 - [:us: en](https://gitlocalize.com/repo/4360/en/src/i18n/resources/en/common.json)
 - [:es: es](https://gitlocalize.com/repo/4360/es/src/i18n/resources/en/common.json)
 - [:iran: fa](https://gitlocalize.com/repo/4360/fa/src/i18n/resources/en/common.json)
 - [:fr: fr](https://gitlocalize.com/repo/4360/fr/src/i18n/resources/en/common.json)
 - [:india: hi](https://gitlocalize.com/repo/4360/hi/src/i18n/resources/en/common.json)
 - [:it: it](https://gitlocalize.com/repo/4360/it/src/i18n/resources/en/common.json)
 - [:jp: ja](https://gitlocalize.com/repo/4360/ja/src/i18n/resources/en/common.json)
 - [:kr: ko](https://gitlocalize.com/repo/4360/ko/src/i18n/resources/en/common.json)
 - [:poland: pl](https://gitlocalize.com/repo/4360/pl/src/i18n/resources/en/common.json)
 - [:portugal: pt](https://gitlocalize.com/repo/4360/pt/src/i18n/resources/en/common.json)
 - [:ru: ru](https://gitlocalize.com/repo/4360/ru/src/i18n/resources/en/common.json)
 - [:tr: tr](https://gitlocalize.com/repo/4360/tr/src/i18n/resources/en/common.json)
 - [:cn: zh](https://gitlocalize.com/repo/4360/zh/src/i18n/resources/en/common.json)


### Schemas

The directory `schemas/` contains JSON schemas which serve as a base for type checking, validation and serialization.

In particular, some of the types:

- are generated from schemas for both Python (as classes) and Typescript (as interfaces)
- are validated on runtime using corresponding libraries in these languages
- are (when appropriate) serialized and deserialized using generated serialization/deserialized functions

We make emphasis on types that are shared across languages (e.g. Python to Typescript) as well as on types that
participate in input-output (e.g. URLs, Local Storage, File I/O) and require particularly careful validation and
serialization.

If you are planning to change one of the types that happens to be generated, you need to modify the corresponding schema
first and them re-run the type generation.

#### See also:

- [JSON Schema website](https://json-schema.org/)
- [Understanding JSON Schema](https://json-schema.org/understanding-json-schema/)

### Release cycle, continuous integration and deployment

TODO

### Getting Started

For new contributers, follow the guide below to learn how to install required software, fork & clone, and submit changes
using a pull request.

#### ✨ Installing Required Software

1. Install Git by following GitHub's instructions
   [here](https://help.github.com/en/github/getting-started-with-github/set-up-git)

2. Node.js can be installed using nvm on [Mac/Linux](https://gist.github.com/d2s/372b5943bce17b964a79) and nvm-windows
   on [Windows](https://docs.microsoft.com/en-us/windows/nodejs/setup-on-windows).

3. Yarn can be globally installed following [these steps](https://classic.yarnpkg.com/en/docs/install/#mac-stable)

#### 🍴 Forking the Repo

Click the Fork button on the upper right-hand side of the repository’s page.

#### 👯 Clone Forked Repository

Clone this repository to your local machine. You can use the URL of your repo inside git command, for example:

```bash
git clone https://github.com/<YOUR_GITHUB_USERNAME>/covid19_scenarios

```

#### 🔨 Start coding!

#### 💻 Updating the Forked Repository

To ensure that the forked code stays updated, you’ll need to add a Git remote pointing back to the original repository
and create a local branch.

```
git remote add upstream https://github.com/neherlab/covid19_scenarios
```

To create and checkout a branch,

1. Create and checkout a branch

```
git checkout -b <new branch name>
```

2. Make changes to the files
3. Commit your changes to the branch using `git add` and then `git commit`

#### 💪 Submitting changes using a Pull Request

To submit your code to the repository, you can
[submit a pull request](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request).

<h1 align="center" />

