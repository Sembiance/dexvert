import fs from 'fs';
import path from 'path';
import util from 'util';
import assert from 'assert';

import yargs from 'yargs';
import {ctrl2smf} from './rcm_converter.js';

// Parses argv by yargs.
const argv = yargs.
	strict().
	options({
		'reset-before-ctrl': {
			type: 'boolean',
			default: true,
			describe: 'Send reset SysEx before sending control files',
		},
		'optimize-ctrl': {
			type: 'boolean',
			default: true,
			describe: 'Optimize redundant SysEx generated from control files',
		},
		'debug': {
			type: 'boolean',
			default: false,
			describe: 'Debug mode (Enable assertion)',
		},
	}).
	demandCommand(1, "Argument 'ctrl-file' is not specified.").
	help().
	alias('h', 'help').
	alias('v', 'version').
	usage('$0 [options] ctrl-file [syx-file]').
	wrap(Math.max(yargs.terminalWidth() - 2, 80)).
	argv;

// Gets the file names from argv.
const ctrlFile = argv._[0];
let   smfFile  = argv._[1];
if (!smfFile) {
	// If the destination file name is not specify, makes it from the source file name.
	const p = path.parse(ctrlFile);
	p.name = p.base;
	p.base = '';
	p.ext = '.mid';
	smfFile = path.format(p);
}

console.assert = (argv.debug) ? assert : () => {/* EMPTY */};

const readFileAsync  = util.promisify(fs.readFile);
const writeFileAsync = util.promisify(fs.writeFile);

// Converts an control file to a syx File.
(async () => {
	try {
		const ctrlData = await readFileAsync(ctrlFile);
		const smfData  = await ctrl2smf(new Uint8Array(ctrlData), path.basename(ctrlFile), argv);
		await writeFileAsync(smfFile, smfData);
	} catch (e) {
		console.error((argv.debug) ? e : `${e}`);
	}
})();
