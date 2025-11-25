import fs from 'fs';
import path from 'path';
import util from 'util';
import assert from 'assert';

import yargs from 'yargs';
import {convertMtdToSysEx, convertCm6ToSysEx, convertGsdToSysEx, isSysExRedundant} from './rcm_ctrl_converter.js';

// Parses argv by yargs.
const argv = yargs.
	strict().
	options({
		'optimize-ctrl': {
			type: 'boolean',
			default: false,
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
let   syxFile  = argv._[1];
if (!syxFile) {
	// If the destination file name is not specify, makes it from the source file name.
	const p = path.parse(ctrlFile);
	p.name = p.base;
	p.base = '';
	p.ext = '.syx';
	syxFile = path.format(p);
}

console.assert = (argv.debug) ? assert : () => {/* EMPTY */};

const readFileAsync  = util.promisify(fs.readFile);
const writeFileAsync = util.promisify(fs.writeFile);

// Converts a control file to a syx File.
(async () => {
	try {
		const bytes = new Uint8Array(await readFileAsync(ctrlFile));
		const allSysExs = convertCm6ToSysEx(bytes) || convertMtdToSysEx(bytes) || convertGsdToSysEx(bytes);
		const sysExs = (argv.optimizeCtrl) ? allSysExs.filter((e) => !isSysExRedundant(e)) : allSysExs;

		await writeFileAsync(syxFile, new Uint8Array([].concat(...sysExs)));
	} catch (e) {
		console.error((argv.debug) ? e : `${e}`);
	}
})();
