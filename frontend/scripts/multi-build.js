// This script builds multiple front end targets
// We need this because the base font size changed from Hawthorn to Juniper

// This for pre-Juniper
process.env.REM_BASE = 10;
process.env.FIGURES_APP_BUILD = '../figures/static/figures/rb10';
require('./build.js');

// This for Juniper (and maybe beyond)
process.env.REM_BASE = 16;
process.env.FIGURES_APP_BUILD = '../figures/static/figures/rb16';
require('./build.js');
