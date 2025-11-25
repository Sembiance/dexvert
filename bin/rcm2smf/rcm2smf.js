import fs from 'node:fs';
import path from 'node:path';
import util from 'node:util';
import assert from 'node:assert';

import yargs from 'yargs';

import {rcm2smf, defaultSettings} from './rcm_converter.js';
import {decodeNec932} from './nec932_decoder.js';

// Options for yargs.
const options = {
	// Common
	'debug': {
		type: 'boolean',
		default: false,
		describe: 'Debug mode (Enable assertion)',
	},

	// About SMF generation
	'meta-text-memo': {
		describe: 'Generate SMF Text events for RCM memo area',
	},
	'meta-text-comment': {
		describe: 'Generate SMF Text events for RCM Comment events',
	},
	'meta-text-usr-exc': {
		describe: 'Generate SMF Text events for each RCM UsrExc events',
	},
	'meta-cue': {
		describe: 'Generate SMF Cue Point events for RCM KeyScan and External Command event',
	},
	'meta-time-signature': {
		describe: 'Generate SMF Time Signature events from each measure\'s step time',
	},
	'trim-track-name': {
		describe: 'Remove whitespace from SMF Sequence/Track Name events',
		choices: ['none', 'left', 'right', 'both'],
	},
	'trim-text-memo': {
		describe: 'Remove whitespace from SMF Text events for RCM memo area',
		choices: ['none', 'left', 'right', 'both'],
	},
	'trim-text-comment': {
		describe: 'Remove whitespace from SMF Text events for RCM Comment events',
		choices: ['none', 'left', 'right', 'both'],
	},
	'trim-text-usr-exc': {
		describe: 'Remove whitespace from SMF Text events for RCM UsrExc events',
		choices: ['none', 'left', 'right', 'both'],
	},
	'note-off': {
		describe: 'Use note-off ("8nH kk uu") events instead of "9nH kk 00H"',
	},
	'note-off-vel': {
		describe: 'Velocity of note-off ("8nH kk uu") events',
	},

	// About RCM parsing
	'st-plus': {
		describe: 'Assume ST+ as signed (>= RCM 2.5) or unsigned (<= RCM 2.3a)',
		choices: ['auto', 'signed', 'unsigned'],
	},
	'reset-before-ctrl': {
		describe: 'Send reset SysEx before sending control files',
	},
	'optimize-ctrl': {
		describe: 'Optimize redundant SysEx generated from control files',
	},
	'extra-sysex-wait': {
		describe: 'Wait for extra time after each SysEx in control files (for MT-32 Ver.1.xx)',
	},
	'ignore-ctrl-file': {
		describe: 'Ignore control files',
	},
	'ignore-out-of-range': {
		describe: 'Ignore out-of-range values in events',
	},
	'ignore-wrong-event': {
		describe: 'Ignore unexpected events',
	},
	'max-loop-nest': {
		describe: 'Maximum loop nest level',
	},
	'infinity-loop-count': {
		describe: 'Loop count to revise to avoid loop-bomb',
	},
	'loop-bomb-threshold': {
		describe: 'Number of extracted beats considered as loop-bomb',
	},
	'roland-dev-id': {
		describe: 'Initial value of device ID for RolDev#',
	},
	'roland-model-id': {
		describe: 'Initial value of model ID for RolDev#',
	},
	'roland-base-addr-h': {
		describe: 'Initial value of Initial value of the base address (H) for RolBase',
	},
	'roland-base-addr-m': {
		describe: 'Initial value of Initial value of the base address (M) for RolBase',
	},
	'yamaha-dev-id': {
		describe: 'Initial value of device ID for YamDev#',
	},
	'yamaha-model-id': {
		describe: 'Initial value of model ID for YamDev#',
	},
	'yamaha-base-addr-h': {
		describe: 'Initial value of Initial value of the base address (H) for YamBase',
	},
	'yamaha-base-addr-m': {
		describe: 'Initial value of Initial value of the base address (M) for YamBase',
	},
};

// Adds type and default value from the default settings defined in rcm_converter.
for (const key of Object.keys(defaultSettings)) {
	const optName = key.replace(/([A-Z])/ug, (s) => `-${s.charAt(0).toLowerCase()}`);
	console.assert(optName in options);
	Object.assign(options[optName], {
		type: typeof defaultSettings[key],
		default: defaultSettings[key],
	});
}

// Parses argv by yargs.
const argv = yargs.
	strict().
	options(options).
	config(defaultSettings).
	config('settings').
	check((argv) => {
		// Checks whether the specified numbers are valid.
		for (const key of Object.keys(argv).filter((e) => typeof argv[e] === 'number')) {
			if (Number.isNaN(argv[key]) || !Number.isInteger(argv[key])) {
				throw new Error(`${key} must be a positive integer number.`);
			}
		}

		// Checks whether the specified numbers are in range.
		const ranges = {
			noteOffVel:        [0, 127],
			maxLoopNest:       [0, 100],
			infinityLoopCount: [1, 255],
			loopBombThreshold: [100, Infinity],
			rolandDevId:       [0, 127],
			rolandModelId:     [0, 127],
			rolandBaseAddrH:   [0, 127],
			rolandBaseAddrM:   [0, 127],
			yamahaDevId:       [0, 127],
			yamahaModelId:     [0, 127],
			yamahaBaseAddrH:   [0, 127],
			yamahaBaseAddrM:   [0, 127],
		};
		for (const key of Object.keys(ranges)) {
			const [min, max] = ranges[key];
			if (argv[key] < min || max < argv[key]) {
				throw new Error(`${key} must be in a range of (${min} - ${max}).`);
			}
		}

		// Initial reset SysEx cannot be omitted when optimizing SysEx generated from control files.
		if (argv.optimizeCtrl && !argv.resetBeforeCtrl) {
			throw new Error(`In case of optimizing SysEx for control files, adding an initial reset SysEx is needed.\n(Use "--reset-before-ctrl" or "--no-optimize-ctrl")`);
		}

		return true;
	}).
	demandCommand(1, "Argument 'rcm-file' is not specified.").
	help().
	alias('h', 'help').
	alias('v', 'version').
	group([
		'meta-text-memo', 'meta-text-comment', 'meta-text-usr-exc', 'meta-cue', 'meta-time-signature',
		'trim-track-name', 'trim-text-memo', 'trim-text-comment', 'trim-text-usr-exc',
		'note-off', 'note-off-vel',
	], 'SMF Generation:').
	group([
		'st-plus',
		'reset-before-ctrl', 'optimize-ctrl', 'extra-sysex-wait', 'ignore-ctrl-file',
		'ignore-out-of-range', 'ignore-wrong-event',
		'max-loop-nest', 'infinity-loop-count', 'loop-bomb-threshold',
		'roland-dev-id', 'roland-model-id', 'roland-base-addr-h', 'roland-base-addr-m',
		'yamaha-dev-id', 'yamaha-model-id', 'yamaha-base-addr-h', 'yamaha-base-addr-m',
	], 'RCM Parsing:').
	usage('$0 [options] rcm-file [smf-file]').
	wrap(Math.max(yargs.terminalWidth() - 2, 80)).
	argv;

// Gets the file names from argv.
const rcmFile = argv._[0];
let   smfFile = argv._[1];
if (!smfFile) {
	// If the destination file name is not specify, makes it from the source file name.
	const p = path.parse(rcmFile);
	p.name = p.base;
	p.base = '';
	p.ext = '.mid';
	smfFile = path.format(p);
}

// Extracts properties which have camel-case name as a settings.
const settings = Object.keys(argv).filter((e) => /^[a-zA-Z0-9]+$/u.test(e)).reduce((p, c) => {
	p[c] = argv[c];
	return p;
}, {});

console.assert = (argv.debug) ? assert : () => {/* EMPTY */};

const readFileAsync  = util.promisify(fs.readFile);
const writeFileAsync = util.promisify(fs.writeFile);

// Converts an RCM file to a Standard MIDI File.
(async () => {
	try {
		const rcmData = await readFileAsync(rcmFile);
		const smfData = await rcm2smf(new Uint8Array(rcmData), fileReader, settings);
		await writeFileAsync(smfFile, smfData);
	} catch (e) {
		console.error((settings.debug) ? e : `${e}`);
	}

	function fileReader(fileName, fileNameRaw) {
		console.assert(fileName, 'Invalid argument');

		const baseDir = path.parse(rcmFile).dir;
		if (/^[\x20-\x7E]*$/u.test(fileName)) {
			return readFileAsync(path.join(baseDir, fileName));

		} else if (fileNameRaw) {
			const fileNameCP932 = decodeNec932(fileNameRaw);
			return readFileAsync(path.join(baseDir, fileNameCP932));

		} else {
			return Promise.reject(new Error('File not found'));
		}
	};
})();
