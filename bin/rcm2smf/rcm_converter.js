import {convertMtdToSysEx, convertCm6ToSysEx, convertGsdToSysEx, isSysExRedundant} from './rcm_ctrl_converter.js';

// Default settings of this converter.
export const defaultSettings = Object.freeze({
	metaTextMemo:      true,
	metaTextComment:   true,
	metaTextUsrExc:    true,
	metaCue:           true,
	metaTimeSignature: true,
	trimTrackName:   'both',
	trimTextMemo:    'none',
	trimTextComment: 'both',
	trimTextUsrExc:  'both',
	noteOff:    false,
	noteOffVel: 64,

	stPlus: 'auto',
	resetBeforeCtrl:  true,
	optimizeCtrl:     true,
	extraSysexWait:   true,
	ignoreCtrlFile:   false,
	ignoreOutOfRange: true,
	ignoreWrongEvent: true,
	maxLoopNest:          5,
	infinityLoopCount:    2,
	loopBombThreshold: 4000,
	rolandDevId:     0x10,
	rolandModelId:   0x16,
	rolandBaseAddrH: 0x00,
	rolandBaseAddrM: 0x10,
	yamahaDevId:     0x10,
	yamahaModelId:   0x4c,
	yamahaBaseAddrH: 0x00,
	yamahaBaseAddrM: 0x00,
});

const EVENT_MCP = Object.freeze({
	UsrExc0:     -1,
	UsrExc1:     -1,
	UsrExc2:     -1,
	UsrExc3:     -1,
	UsrExc4:     -1,
	UsrExc5:     -1,
	UsrExc6:     -1,
	UsrExc7:     -1,
	TrExcl:      -1,
	ExtCmd:      -1,
	DX7FUNC:   0xc0,	// DX7 Function
	DX_PARA:   0xc1,	// DX Voice Parameter
	DX_PERF:   0xc2,	// DX Performance
	TX_FUNC:   0xc3,	// TX Function
	FB_01_P:   0xc5,	// FB-01 Parameter
	FB_01_S:   0xc6,	// FB-01 System Parameter
	TX81Z_V:   0xc7,	// TX81Z VCED
	TX81Z_A:   0xc8,	// TX81Z ACED
	TX81Z_P:   0xc9,	// TX81Z PCED
	TX81Z_S:   0xca,	// TX81Z System
	TX81Z_E:   0xcb,	// TX81Z Effect
	DX7_2_R:   0xcc,	// DX7-2 Remote SW
	DX7_2_A:   0xcd,	// DX7-2 ACED
	DX7_2_P:   0xce,	// DX7-2 PCED
	TX802_P:   0xcf,	// TX802 PCED
	YamBase:     -1,
	YamDev:      -1,
	YamPara:     -1,
	XGPara:      -1,
	MKS_7:       -1,
	RolBase:   0xe7,	// MT32BASE
	RolPara:   0xe8,	// MT32PARA
	RolDev:    0xe6,	// R.EXCLU
	BankPrgL:    -1,
	BankPrg:     -1,
	KeyScan:     -1,
	MIDI_CH:   0xd0,	// MIDI Channel Change
	TEMPO:     0xfa,	// Relative Tempo Change
	AFTER_C:   0xe3,	// After Touch (Ch.)
	CONTROL:   0xe2,	// Control Change
	PROGRAM:     -1,
	AFTER_K:   0xe1,	// After Touch (Poly)
	PITCH:     0xe4,	// Pitch Bend Change
	MusicKey:    -1,	// TODO: Investigate whether F2 event is for MusicKey or not.
	Comment:     -1,
	SecondEvt:   -1,
	LoopEnd:   0xfb,	// Loop End
	LoopStart: 0xfc,	// Loop Start
	SameMeas:    -1,
	MeasEnd:   0xfd,	// Measure End
	TrackEnd:  0xfe,	// End of Track
	CMU_800:   0xf9,	// CMU-800
	UserPrg:   0xe0,	// Program Change (User Program)
});

const EVENT_RCP = Object.freeze({
	UsrExc0:   0x90,	// User Exclusive 0
	UsrExc1:   0x91,	// User Exclusive 1
	UsrExc2:   0x92,	// User Exclusive 2
	UsrExc3:   0x93,	// User Exclusive 3
	UsrExc4:   0x94,	// User Exclusive 4
	UsrExc5:   0x95,	// User Exclusive 5
	UsrExc6:   0x96,	// User Exclusive 6
	UsrExc7:   0x97,	// User Exclusive 7
	TrExcl:    0x98,	// Track Exclusive
	ExtCmd:    0x99,	// External Command
	DX7FUNC:   0xc0,	// DX7 Function
	DX_PARA:   0xc1,	// DX Voice Parameter
	DX_PERF:   0xc2,	// DX Performance
	TX_FUNC:   0xc3,	// TX Function
	FB_01_P:   0xc5,	// FB-01 Parameter
	FB_01_S:   0xc6,	// FB-01 System Parameter
	TX81Z_V:   0xc7,	// TX81Z VCED
	TX81Z_A:   0xc8,	// TX81Z ACED
	TX81Z_P:   0xc9,	// TX81Z PCED
	TX81Z_S:   0xca,	// TX81Z System
	TX81Z_E:   0xcb,	// TX81Z Effect
	DX7_2_R:   0xcc,	// DX7-2 Remote SW
	DX7_2_A:   0xcd,	// DX7-2 ACED
	DX7_2_P:   0xce,	// DX7-2 PCED
	TX802_P:   0xcf,	// TX802 PCED
	YamBase:   0xd0,	// Yamaha Base Address
	YamDev:    0xd1,	// Yamaha Dev# & Model ID
	YamPara:   0xd2,	// Yamaha Address & Parameter
	XGPara:    0xd3,	// Yamaha XG Address & Parameter
	MKS_7:     0xdc,	// Roland MKS-7
	RolBase:   0xdd,	// Roland Base Address
	RolPara:   0xde,	// Roland Address & Parameter
	RolDev:    0xdf,	// Roland Dev# & Model ID
	BankPrgL:  0xe1,	// Program Bank Change (LSB)
	BankPrg:   0xe2,	// Program Bank Change (MSB)
	KeyScan:   0xe5,	// Key Scan
	MIDI_CH:   0xe6,	// MIDI Channel Change
	TEMPO:     0xe7,	// Relative Tempo Change
	AFTER_C:   0xea,	// After Touch (Ch.)
	CONTROL:   0xeb,	// Control Change
	PROGRAM:   0xec,	// Program Change
	AFTER_K:   0xed,	// After Touch (Poly)
	PITCH:     0xee,	// Pitch Bend Change
	MusicKey:  0xf5,	// Music Key
	Comment:   0xf6,	// Comment
	SecondEvt: 0xf7,	// 2nd Event for Comment, TrExcl, and ExtCmd
	LoopEnd:   0xf8,	// Loop End
	LoopStart: 0xf9,	// Loop Start
	SameMeas:  0xfc,	// Same Measure
	MeasEnd:   0xfd,	// Measure End
	TrackEnd:  0xfe,	// End of Track
	CMU_800:     -1,
	UserPrg:     -1,
});

export async function rcm2smf(buf, controlFileReader, options) {
	// Checks the arguments.
	if (!buf || !buf.length) {
		throw new Error(`Invalid argument: ${buf}`);
	}

	// Converts from RCP/G36 to SMF.
	const rcm = await parseRcm(buf, controlFileReader, options);
	const seq = convertRcmToSeq(rcm, options);
	const smf = convertSeqToSmf(seq, rcm.header.timeBase, options);

	return smf;
}

export function ctrl2smf(buf, title, options) {
	// Checks the arguments.
	if (!buf || !buf.length) {
		throw new Error(`Invalid argument: ${buf}`);
	}

	// Makes a dummy (empty) rcm object.
	const rcm = {
		header: {
			title: new Uint8Array(String(title).split('').map((e) => e.charCodeAt())),
			timeBase: 48,
			tempo: 120,
			beatN: 4,
			beatD: 4,
			maxTracks: 0,
		},
		tracks: [],
	};

	// Converts from MCP/CM6/GSD to SysExs.
	let sysExs = convertCm6ToSysEx(buf) || convertMtdToSysEx(buf);
	if (sysExs) {
		rcm.header.sysExsCM6 = sysExs;	// Handles MTD as CM6 to avoid particularities of MCP.
	} else {
		sysExs = convertGsdToSysEx(buf);
		if (sysExs) {
			rcm.header.sysExsGSD = sysExs;
		} else {
			throw new Error('Invalid control file');
		}
	}

	// Converts from the generated rcm object to SMF.
	const seq = convertRcmToSeq(rcm, options);
	const smf = convertSeqToSmf(seq, rcm.header.timeBase, options);

	return smf;
}

export async function parseRcm(buf, controlFileReader, options) {
	// Checks the arguments.
	if (!buf || !buf.length) {
		throw new Error(`Invalid argument: ${buf}`);
	}

	// Makes a settings object from the default settings and the specified ones.
	const settings = {...defaultSettings, ...options};

	// Parses the data as RCP format. If it failed, parses it again as G36 format. If it failed again, tries MCP parser.
	const rcm = parseRcp(buf) || parseG36(buf) || parseMcp(buf);
	if (!rcm) {
		throw new Error('Not Recomposer file');
	}

	// Reads and parses control files.
	for (const kind of ['MTD', 'CM6', 'GSD', 'GSD2']) {
		if (settings.ignoreCtrlFile) {
			break;
		}

		const keyName  = `fileName${kind}`;
		const keyData  = `fileData${kind}`;
		const keySysEx = `sysExs${kind}`;

		if (!rcm.header[keyName] || rcm.header[keyName].length === 0) {
			continue;
		}

		// Checks whether the control file reader is provided.
		if (!controlFileReader) {
			throw new Error('Control file reader is not specified');
		}

		// Reads the control file.
		const fileName = String.fromCharCode(...rcm.header[keyName]);
		const buf = await controlFileReader(fileName, (/^[\x20-\x7E]*$/u.test(fileName)) ? undefined : rcm.header[keyName]).catch((e) => {
			throw new Error(`Control file not found: ${fileName}${(settings.debug) ? `\n${e}` : ''}`);
		});

		// Parses the control file.
		console.assert(buf);
		const sysExs = {
			MTD:  convertMtdToSysEx,
			CM6:  convertCm6ToSysEx,
			GSD:  convertGsdToSysEx,
			GSD2: convertGsdToSysEx,
		}[kind](buf);
		if (!sysExs) {
			throw new Error(`Not ${kind.slice(0, 3)} file: ${fileName}`);
		}

		rcm.header[keyData]  = buf;
		rcm.header[keySysEx] = sysExs;

		// Gets Patch Memory information for user patches.
		if (kind === 'MTD') {
			const patches = sysExs.filter((e) => {
				// Extracts SysExs regarding Patch Memory. (#1-#128)
				console.assert(e[0] === 0xf0 && e[1] === 0x41 && e[2] === 0x10 && e[3] === 0x16 && e[4] === 0x12);
				return (e[5] === 0x05);	// Address '05 xx xx' is for Patch Memory
			}).reduce((p, c) => {
				// Splits payloads of SysExs by 8-byte.
				console.assert(c.length > 5 + 3 + 2);
				for (let i = 5 + 3; i < c.length; i += 8) {
					const e = c.slice(i, i + 8);
					if (e.length === 8) {
						p.push(e);
					}
				}
				return p;
			}, []);
			console.assert(patches.length === 192);
			rcm.header.patches = patches;
		}
	}

	// Executes post-processing for each track.
	if (!rcm.header.isMCP) {
		// For RCP/G36
		for (const track of rcm.tracks) {
			// Sets MIDI channel No. and port No.
			track.chNo   = (track.midiCh >= 0) ? track.midiCh % 16 : -1;
			track.portNo = (track.midiCh >= 0) ? Math.trunc(track.midiCh / 16) : 0;

			// Reinterprets ST+ if necessary.
			if (!rcm.header.isF && !rcm.header.isG) {
				console.assert('stShiftS' in track && 'stShiftU' in track);
				if (settings.stPlus === 'signed') {
					if (track.stShiftS !== track.stShift && (track.stShiftS < -99 || 99 < track.stShiftS)) {
						console.warn(`ST+ has been converted to signed as specified. (${track.stShift} -> ${track.stShiftS}) But, it seems to be unsigned.`);
					}
					track.stShift = track.stShiftS;
				} else if (settings.stPlus === 'unsigned') {
					track.stShift = track.stShiftU;
				}
			}

			// Extracts same measures and loops.
			track.extractedEvents = extractEvents(track.events, rcm.header.timeBase, false, settings);
		}
	} else {
		// For MCP
		for (const track of rcm.tracks.slice(1, -1)) {
			// Sets MIDI channel No.
			track.chNo = (track.midiCh >= 0) ? track.midiCh : -1;

			// Extracts loops.
			track.extractedEvents = extractEvents(track.events, rcm.header.timeBase, true, settings);
		}

		// Extracts rhythm track.
		console.assert(rcm.tracks.length >= 10);
		const seqTrack     = rcm.tracks[9];
		const patternTrack = rcm.tracks[0];

		seqTrack.chNo = seqTrack.midiCh;
		seqTrack.extractedEvents = extractRhythm(seqTrack.events, patternTrack.events, settings);
	}

	return rcm;
}

export function parseMcp(buf) {
	// Checks the arguments.
	if (!buf || !buf.length) {
		throw new Error(`Invalid argument: ${buf}`);
	}

	// Checks the file header.
	// Note: Confirmed 3 types of header: 'M1', 'MC', and [0x00, 0x00]
	if (buf.length < 256) {
		return null;
	}
	const id = buf.slice(0x00, 0x02);
	if (!/^(?:M1|MC)$/u.test(String.fromCharCode(...id)) && !(id[0] === 0x00 && id[1] === 0x00)) {
		return null;
	}

	const view = new DataView(buf.buffer, buf.byteOffset);
	const rcm = {header: {isMCP: true, maxTracks: 1 + 8 + 1}, tracks: []};

	// Header
	rcm.header.title = buf.slice(0x02, 0x20);

	rcm.header.timeBase = view.getUint8(0x20);
	rcm.header.tempo    = view.getUint8(0x21);
	rcm.header.beatN    = view.getUint8(0x22);
	rcm.header.beatD    = view.getUint8(0x23);
	rcm.header.key      = view.getUint8(0x24);

	if (buf[0x60] !== 0x00 && buf[0x60] !== 0x20) {
		rcm.header.fileNameMTD = new Uint8Array([...rawTrim(rawTrimNul(buf.slice(0x60, 0x66))), '.'.codePointAt(), ...rawTrim(rawTrimNul(buf.slice(0x66, 0x69)))]);
	}

	// Tracks
	rcm.tracks = [...new Array(rcm.header.maxTracks)].map((_, i) => {
		const track = {events: []};
		if (i > 0) {
			track.midiCh = view.getInt8(0x40 + i - 1);
			track.isCMU  = (buf[0x50 + i - 1] !== 0);
			track.memo   = buf.slice(0x70 + (i - 1) * 16, 0x70 + i * 16);
		}
		return track;
	});

	// All events
	const events = buf.slice(0x0100).reduce((p, _, i, a) => {
		if (i % 4 === 0) {
			p.push(a.slice(i, i + 4));
		}
		return p;
	}, []);
	if (events[events.length - 1].length !== 4) {
		events.pop();
	}

	// Separates all the events into each track.
	let trackNo = 0;
	for (const event of events) {
		console.assert(Array.isArray(rcm.tracks[trackNo].events));
		rcm.tracks[trackNo].events.push(event);

		if (event[0] === EVENT_MCP.TrackEnd) {
			trackNo++;
			if (trackNo >= rcm.header.maxTracks) {
				break;
			}
		}
	}

	return rcm;
}

export function parseRcp(buf) {
	// Checks the arguments.
	if (!buf || !buf.length) {
		throw new Error(`Invalid argument: ${buf}`);
	}

	// Checks the file header.
	if (buf.length < 518 || !String.fromCharCode(...buf.slice(0x0000, 0x0020)).startsWith('RCM-PC98V2.0(C)COME ON MUSIC')) {
		return null;
	}

	const view = new DataView(buf.buffer, buf.byteOffset);
	const rcm = {header: {}, tracks: []};

	// Header
	rcm.header.title = buf.slice(0x0020, 0x0060);
	rcm.header.memoLines = [...new Array(12)].map((_, i) => buf.slice(0x0060 + 28 * i, 0x0060 + 28 * (i + 1)));

	rcm.header.timeBase = (view.getUint8(0x01e7) << 8) | view.getUint8(0x01c0);
	rcm.header.tempo    = view.getUint8(0x01c1);
	rcm.header.beatN    = view.getUint8(0x01c2);
	rcm.header.beatD    = view.getUint8(0x01c3);
	rcm.header.key      = view.getUint8(0x01c4);
	rcm.header.playBias = view.getInt8(0x01c5);

	rcm.header.fileNameCM6 = rawTrim(rawTrimNul(buf.slice(0x01c6, 0x01d2)));
	rcm.header.fileNameGSD = rawTrim(rawTrimNul(buf.slice(0x01d6, 0x01e2)));

	const trackNum = view.getUint8(0x01e6);
	rcm.header.maxTracks = (trackNum === 0) ? 18 : trackNum;
	rcm.header.isF = (trackNum !== 0);

	rcm.header.userSysExs = [...new Array(8)].map((_, i) => {
		const index = 0x0406 + 48 * i;
		return {
			memo:  buf.slice(index, index + 24),
			bytes: buf.slice(index + 24, index + 48),
		};
	});

	// Tracks
	const HEADER_LENGTH = 44;
	const EVENT_LENGTH  = 4;
	let index = 0x0586;
	for (let i = 0; i < rcm.header.maxTracks && index + HEADER_LENGTH < buf.length; i++) {
		// If the footer data found, terminates the loop.
		if (String.fromCharCode(...buf.slice(index, index + 4)).startsWith('RCFW')) {
			break;
		}

		const track = {};

		// Track header
		let size = view.getUint16(index, true);
		if (size < HEADER_LENGTH || index + size > buf.length) {
			console.warn(`Invalid track size: ${size}`);
			break;
		}

		track.trackNo  = view.getUint8(index + 2);
		track.midiCh   = view.getInt8(index + 4);
		track.keyShift = view.getUint8(index + 5);
		track.stShiftS = view.getInt8(index + 6);
		track.stShiftU = view.getUint8(index + 6);
		track.mode     = view.getUint8(index + 7);
		track.memo     = buf.slice(index + 8, index + 44);

		// Track events
		let events = buf.slice(index + HEADER_LENGTH, index + size).reduce((p, _, i, a) => {
			if (i % EVENT_LENGTH === 0) {
				const event = a.slice(i, i + EVENT_LENGTH);
				p.push(event);
			}
			return p;
		}, []);

		// Checks whether the last event is End of Track to judge the track size information is reliable or not.
		// If the track size information seems to be wrong, gets actual size by End of Track event.
		// Note 1: A very few RCP files contain unknown "FF xx xx xx" event as if it is End of Track.
		// Note 2: STed2 (a Recomposer clone) seems to treat 16-bit track size information as 18-bit
		// by using unused lower 2-bit. But, this program doesn't follow to such unofficial extension.
		const lastEvent = events[events.length - 1];
		if ((lastEvent[0] !== 0xfe && lastEvent[0] !== 0xff) || lastEvent.length !== EVENT_LENGTH) {
			// Track events
			let isEot = false;
			events = buf.slice(index + HEADER_LENGTH, buf.length).reduce((p, _, i, a) => {
				if (i % EVENT_LENGTH === 0 && !isEot) {
					const event = a.slice(i, i + EVENT_LENGTH);
					if (event.length === EVENT_LENGTH) {
						p.push(event);
						if (event[0] === 0xfe || event[0] === 0xff) {
							isEot = true;
						}
					}
				}
				return p;
			}, []);

			// Track size
			const actualSize = HEADER_LENGTH + EVENT_LENGTH * events.length;
			if (size !== actualSize) {
				console.warn(`Track size information doesn't match the actual size: (${size} -> ${actualSize})`);
			}
			size = actualSize;
		}

		track.events = events;

		rcm.tracks.push(track);

		index += size;
	}

	// Sets ST+ for each track.
	const isStSigned = rcm.header.isF || rcm.tracks.every((track) => (-99 <= track.stShiftS && track.stShiftS <= 99));
	rcm.tracks.forEach((track) => {
		track.stShift = (isStSigned) ? track.stShiftS : track.stShiftU;
	});

	return rcm;
}

export function parseG36(buf) {
	// Checks the arguments.
	if (!buf || !buf.length) {
		throw new Error(`Invalid argument: ${buf}`);
	}

	// Checks the file header.
	if (buf.length < 518 || !String.fromCharCode(...buf.slice(0x0000, 0x0020)).startsWith('COME ON MUSIC RECOMPOSER RCP3.0')) {
		return null;
	}

	const view = new DataView(buf.buffer, buf.byteOffset);
	const rcm = {header: {isG: true}, tracks: []};

	// Header
	rcm.header.title = buf.slice(0x0020, 0x0060);
	rcm.header.memoLines = [...new Array(12)].map((_, i) => buf.slice(0x00a0 + 30 * i, 0x00a0 + 30 * (i + 1)));

	rcm.header.maxTracks = view.getUint16(0x0208, true);
	rcm.header.timeBase  = view.getUint16(0x020a, true);
	rcm.header.tempo     = view.getUint16(0x020c, true);
	rcm.header.beatN     = view.getUint8(0x020e);
	rcm.header.beatD     = view.getUint8(0x020f);
	rcm.header.key       = view.getUint8(0x0210);
	rcm.header.playBias  = view.getInt8(0x0211);

	rcm.header.fileNameGSD  = rawTrim(rawTrimNul(buf.slice(0x0298, 0x02a8)));
	rcm.header.fileNameGSD2 = rawTrim(rawTrimNul(buf.slice(0x02a8, 0x02b8)));
	rcm.header.fileNameCM6  = rawTrim(rawTrimNul(buf.slice(0x02b8, 0x02c8)));

	rcm.header.userSysExs = [...new Array(8)].map((_, i) => {
		const index = 0x0b18 + 48 * i;
		return {
			memo:  buf.slice(index, index + 23),
			bytes: buf.slice(index + 23, index + 48),
		};
	});

	// Tracks
	const HEADER_LENGTH = 46;
	const EVENT_LENGTH  = 6;
	let index = 0x0c98;
	for (let i = 0; i < rcm.header.maxTracks && index + HEADER_LENGTH < buf.length; i++) {
		// If the footer data found, terminates the loop.
		if (String.fromCharCode(...buf.slice(index, index + 4)).startsWith('RCFW')) {
			break;
		}

		const track = {};

		// Track header
		const size = view.getUint32(index, true);
		if (size < HEADER_LENGTH || index + size > buf.length) {
			console.warn(`Invalid track size: ${size}`);
			break;
		}

		track.trackNo  = view.getUint8(index + 4);
		track.midiCh   = view.getInt8(index + 6);
		track.keyShift = view.getUint8(index + 7);
		track.stShift  = view.getInt8(index + 8);
		track.mode     = view.getUint8(index + 9);
		track.memo     = buf.slice(index + 10, index + 46);

		// Track events
		track.events = buf.slice(index + HEADER_LENGTH, index + size).reduce((p, _, i, a) => {
			if (i % EVENT_LENGTH === 0) {
				p.push(a.slice(i, i + EVENT_LENGTH));
			}
			return p;
		}, []);

		rcm.tracks.push(track);

		index += size;
	}

	return rcm;
}

function extractEvents(events, timeBase, isMCP, settings) {
	console.assert(Array.isArray(events), 'Invalid argument', {events});
	console.assert(timeBase > 0, 'Invalid argument', {timeBase});
	console.assert(settings, 'Invalid argument', {settings});

	if (events.length === 0) {
		return [];
	}

	// Sets constants and chooses event parser.
	const EVENT = (isMCP) ? EVENT_MCP : EVENT_RCP;
	const EVENT_LENGTH = events[0].length;
	console.assert(EVENT_LENGTH === 4 || EVENT_LENGTH === 6, 'Event length must be 4 or 6', {EVENT_LENGTH});
	console.assert(events.every((e) => e.length === EVENT_LENGTH), 'All of events must be same length', {events});
	const HEADER_LENGTH = (isMCP) ? NaN      : (EVENT_LENGTH === 4) ? 44 : 46;
	const convertEvent  = (isMCP) ? (e) => e : (EVENT_LENGTH === 4) ? convertEvent4byte : convertEvent6byte;

	// Extracts same measures and loops.
	const extractedEvents = [];
	const stacks = [];
	let lastIndex = -1;
	for (let index = 0; index < events.length;) {
		const event = convertEvent(events[index]);

		// Resolves Same Measure event.
		if (event[0] === EVENT.SameMeas) {
			// If it is already in Same Measure mode, quits Same Measure.
			if (lastIndex >= 0) {
				// Leaves Same Measure mode and goes backs to the previous position.
				index = lastIndex + 1;
				lastIndex = -1;

				// Adds a dummy End Measure event.
				extractedEvents.push([EVENT.MeasEnd, 0x00, 0xfc, 0x01]);

			} else {
				// Enters Same Measure mode.
				lastIndex = index;

				// If the previous event isn't an End Measure event, adds a dummy End Measure event.
				if (index > 0 && events[index - 1][0] !== EVENT.MeasEnd && events[index - 1][0] !== EVENT.SameMeas) {
					extractedEvents.push([EVENT.MeasEnd, 0x00, 0xfc, 0x02]);
				}

				// Moves the current index to the measure.	// TODO: Avoid infinity loop
				let counter = 0;
				while (events[index][0] === EVENT.SameMeas) {
					const [cmd, measure, offset] = convertEvent(events[index]);
					console.assert(cmd === EVENT.SameMeas, {cmd, measure, offset});

					index = (offset - HEADER_LENGTH) / EVENT_LENGTH;
					validateAndThrow(Number.isInteger(index) && (0 <= index && index < events.length), `Invalid Same Measure event: ${{cmd, measure, offset}}`);

					counter++;
					validateAndThrow(counter < 100, `Detected infinity Same Measure reference.`);
				}
			}
			continue;
		}

		// Handles a special event or just adds a normal event to the event array.
		switch (event[0]) {
		case EVENT.SameMeas:
			console.assert(false, 'Same Measure event must be resolved', {event});
			break;

		case EVENT.LoopStart:
			if (stacks.length < settings.maxLoopNest) {
				stacks.push({index, lastIndex,
					count: -1,
					extractedIndex: (extractedEvents.length > 0) ? extractedEvents.length - 1 : 0,
				});
			} else {
				console.warn(`Detected more than ${settings.maxLoopNest}-level of nested loops. Skipped.`);
			}
			index++;
			break;

		case EVENT.LoopEnd:
			if (stacks.length > 0) {
				const lastStack = stacks[stacks.length - 1];

				// If it is a first Loop End event, sets a counter value to it.
				if (lastStack.count < 0) {
					// Checks whether the loop is infinite and revises the number of loops if necessary.
					if (event[1] > 0) {
						lastStack.count = event[1];
					} else {
						console.warn(`Detected an infinite loop. Set number of loops to ${settings.infinityLoopCount}.`);
						lastStack.count = settings.infinityLoopCount;
					}

					// Checks whether it would be a "loop bomb" and revises the number of loops if necessary.
					// Note: "0xf5" means Musickey of RCP. As for RCP, >=0xf5 events don't have ST. But, as for MCP, TEMPO event (0xfa) also has ST. Won't fix.
					const beatNum = extractedEvents.slice(lastStack.extractedIndex).reduce((p, c) => ((c[0] < 0xf5) ? p + c[1] : p), 0) / timeBase;
					if (beatNum * lastStack.count >= settings.loopBombThreshold && lastStack.count > settings.infinityLoopCount) {
						console.warn(`Detected a loop bomb. Set number of loops to ${settings.infinityLoopCount}.`);
						lastStack.count = settings.infinityLoopCount;
					}
				}

				// Decrements the loop counter and moves the index up to the counter.
				lastStack.count--;
				if (lastStack.count > 0) {
					index = lastStack.index + 1;
					lastIndex = lastStack.lastIndex;
				} else {
					const _ = stacks.pop();
					console.assert(_.count === 0, {stacks});
					console.assert(_.lastIndex === lastStack.lastIndex, {stacks});
					index++;
				}

			} else {
				console.warn(`Detected a dangling Loop End event. Skipped.`);
				index++;
			}
			break;

		case EVENT.TrackEnd:
			if (stacks.length > 0) {
				console.warn(`Detected ${stacks.length}-level of unclosed loop. Skipped.`);
			}
			/* FALLTHRU */
		case EVENT.MeasEnd:
			if (lastIndex >= 0) {
				index = lastIndex + 1;
				lastIndex = -1;
			} else {
				index++;
			}
			extractedEvents.push([...event]);
			break;

		case EVENT.TrExcl:
		case EVENT.ExtCmd:
		case EVENT.Comment:
			{
				// Concatenates trailing F7 events.
				const longEvent = [...event];
				index++;

				if (events[index][0] !== EVENT.SecondEvt && event[0] === EVENT.TrExcl) {
					console.warn(`Detected an empty Tr.Excl event: [${hexStr(events[index - 1])}], [${hexStr(events[index])}], ...`);
				}

				while (events[index][0] === EVENT.SecondEvt) {
					longEvent.push(...convertEvent(events[index]).slice(1));
					index++;
				}

				// Trims trailing 0xf7.
				const end = String.fromCharCode(...longEvent).replace(/\xf7+$/u, '').length;
				extractedEvents.push(longEvent.slice(0, end));
			}
			break;

		case EVENT.SecondEvt:
			((settings.ignoreWrongEvent) ? validateAndIgnore : validateAndThrow)(false, `Detected an unexpected F7 event: [${hexStr(events[index])}]`);
			index++;
			break;

		default:
			extractedEvents.push([...event]);
			index++;
			break;
		}
	}

	return extractedEvents;

	function convertEvent4byte(bytes) {
		console.assert(bytes && bytes.length && bytes.length === 4, 'Invalid argument', {bytes});

		if (bytes[0] === EVENT_RCP.Comment || bytes[0] === EVENT_RCP.SecondEvt) {
			return [bytes[0], bytes[2], bytes[3]];
		} else if (bytes[0] === EVENT_RCP.SameMeas) {
			const measure = bytes[1] | ((bytes[2] & 0x03) << 8);
			const offset = (bytes[2] & 0xfc) | (bytes[3] << 8);
			return [bytes[0], measure, offset];
		} else {
			return [...bytes];
		}
	}
	function convertEvent6byte(bytes) {
		console.assert(bytes && bytes.length && bytes.length === 6, 'Invalid argument', {bytes});

		if (bytes[0] === EVENT_RCP.Comment || bytes[0] === EVENT_RCP.SecondEvt) {
			return [...bytes];
		} else if (bytes[0] === EVENT_RCP.SameMeas) {
			const measure = bytes[2] | (bytes[3] << 8);
			const offset = (bytes[4] | (bytes[5] << 8)) * 6 - 0xf2;
			return [bytes[0], measure, offset];
		} else {
			return [bytes[0], bytes[2] | (bytes[3] << 8), bytes[4] | (bytes[5] << 8), bytes[1]];
		}
	}
}

function extractRhythm(seqEvents, patternEvents, settings) {
	console.assert(Array.isArray(seqEvents), 'Invalid argument', {seqEvents});
	console.assert(Array.isArray(patternEvents), 'Invalid argument', {patternEvents});
	console.assert(settings, 'Invalid argument', {settings});

	const validate = (settings.ignoreWrongEvent) ? (isValid, message) => validateAndIgnore(isValid, message) : (isValid, message) => validateAndThrow(isValid, message);

	// Rhythm pattern track
	const patterns = patternEvents.reduce((p, c, i, a) => {
		if (i % (16 + 1) === 0 && c[0] !== EVENT_MCP.TrackEnd) {
			const pattern = a.slice(i, i + 16);
			if (validate(pattern.length === 16 && a[i + 16][0] === EVENT_MCP.MeasEnd, `Invalid rhythm pattern.`)) {
				p.push(pattern);
			} else {
				// Adds a dummy data.
				p.push([...[...new Array(16)].map((_) => [0x00, 0x00, 0x00, 0x00])]);
			}
		}
		return p;
	}, []);

	// Sequence track
	const extractedEvents = [];
	for (const seq of seqEvents) {
		if (seq[0] === EVENT_MCP.TrackEnd) {
			break;
		}

		// Chooses a rhythm pattern.
		const [patternNo, ...velValues] = seq;
		const pattern = patterns[patternNo - 1];

		// Extracts the rhythm pattern with velocity data from sequence track.
		if (validate(pattern, `Invalid rhythm pattern No.${patternNo}: [${hexStr(seq)}]`)) {
			for (const shot of pattern) {
				const st = shot[3];
				const velBits = shot.slice(0, 3).reduce((p, c) => {
					p.push(...[(c >> 6) & 0x03, (c >> 4) & 0x03, (c >> 2) & 0x03, c & 0x03]);
					return p;
				}, []);

				const events = velBits.reduce((p, c, i) => {
					if (c > 0) {
						const event = [
							//  BD, SD, LT, MT, HT, RS, HC, CH, OH, CC, RC
							[0, 36, 38, 41, 45, 48, 37, 39, 42, 46, 49, 51][i],	// Note No.
							0,					// Step time
							1,					// Gate time
							velValues[c - 1],	// Velocity
						];
						p.push(event);
					}
					return p;
				}, []);
				events.push([0, st, 0, 0]);	// For step time

				extractedEvents.push(...events);
			}

			// Adds a dummy End Measure event.
			extractedEvents.push([EVENT_MCP.MeasEnd, 0x00, 0xfd, 0x01]);
		}
	}

	return extractedEvents;
}

function calcSetupMeasureTick(beatN, beatD, timeBase, minTick) {
	console.assert(Number.isInteger(Math.log2(beatD)), 'Invalid argument', {beatD});

	const requiredTick = ((beatN === 3 && beatD === 4) || (beatN === 6 && beatD === 8)) ? timeBase * 3 : timeBase * 4;
	const unit = beatN * timeBase * 4 / beatD;

	let setupTick = unit * Math.trunc(requiredTick / unit);
	while (setupTick < requiredTick || setupTick < minTick) {
		setupTick += unit;
	}

	console.assert(Number.isInteger(setupTick));
	return setupTick;
}

function spaceEachSysEx(sysExs, maxTick, timeBase, isOldMt32) {
	console.assert(sysExs && sysExs.length, 'Invalid argument', {sysExs});
	console.assert(sysExs.length <= maxTick, 'Too many SysEx', {sysExs});
	console.assert(maxTick >= timeBase, 'Too small tick time', {maxTick, timeBase});

	// Calculates the time required for sending and executing each of SysEx.
	const timings = sysExs.map((sysEx) => {
		// Transmit time of SysEx
		let usec = sysEx.length * (8 + 1 + 1) * 1000 * 1000 / 31250.0;

		// Additional wait time
		const [tmpF0, mfrId, deviceId, modelId, command, addrH, addrM, addrL, ...rest] = sysEx;
		console.assert(tmpF0 === 0xf0);
		console.assert(rest[rest.length - 1] === 0xf7);
		let isReset = false;
		if (mfrId === 0x41 && deviceId === 0x10 && command === 0x12) {
			switch (modelId) {
			case 0x16:	// MT-32/CM-64
				if (addrH === 0x7f) {
					// Waits for reset.
					if (isOldMt32) {
						// MT-32 Ver.1.xx requires 420 msec of delay after All Parameters Reset.
						// Note: If the wait time is too short, "Exc. Buffer overflow" error occurs when receiving next SysEx. (confirmed on MT-32 Ver.1.07)
						usec += 420 * 1000;
					} else {
						// No basis for the wait time. Makes it same as GS reset.
						usec += 50 * 1000;
					}
					isReset = true;
				} else if ((0x00 < addrH && addrH <= 0x20) && isOldMt32) {
					// MT-32 Ver.1.xx requires 40 msec of delay between SysExs.
					usec += 40 * 1000;
				} else {
					// DT1 needs more than 20 msec time interval.
					usec += 20 * 1000;
				}
				break;
			case 0x42:	// GS
				if (addrH === 0x40 && addrM === 0x00 && addrL === 0x7f) {
					// Waits for GS reset.
					usec += 50 * 1000;
					isReset = true;
				} else {
					// DT1 needs more than 20 msec time interval.
					usec += 20 * 1000;
				}
				break;
			default:
				console.assert(false);
				break;
			}
		}

		return {sysEx, usec, isReset};
	});

	// Calculates each tick time from the ratio of the time of each SysEx to the total time of SysEx.
	const totalUsec = timings.reduce((p, c) => p + c.usec, 0);
	timings.forEach((e) => {
		e.tick = Math.max(Math.trunc(e.usec * maxTick / totalUsec), 1);
		e.usecPerBeat = e.usec * timeBase / e.tick;
	});

	// Decreases each tick time to set all SysEx with in given time frame.
	while (getTotalTick(timings) > maxTick) {
		const minUsecPerBeat = Math.min(...timings.filter((e) => e.tick > 1).map((e) => e.usecPerBeat));
		timings.filter((e) => e.usecPerBeat === minUsecPerBeat).forEach((e) => {
			e.tick--;
			console.assert(e.tick > 0);
			e.usecPerBeat = e.usec * timeBase / e.tick;
		});
	}

	// Increases each tick time to make tempo faster as much as possible.
	while (getTotalTick(timings) < maxTick) {
		const maxUsecPerBeat = Math.max(...timings.map((e) => e.usecPerBeat));
		const elems = timings.filter((e) => e.usecPerBeat === maxUsecPerBeat);
		if (getTotalTick(timings) + elems.length > maxTick) {
			break;
		}
		elems.forEach((e) => {
			e.tick++;
			e.usecPerBeat = e.usec * timeBase / e.tick;
		});
	}

	return timings;

	function getTotalTick(timings) {
		return timings.reduce((p, c) => p + c.tick, 0);
	}
}

function getMeasureSt(rcm) {
	console.assert(rcm);
	console.assert(EVENT_RCP.MeasEnd  === EVENT_MCP.MeasEnd);
	console.assert(EVENT_RCP.TrackEnd === EVENT_MCP.TrackEnd);

	// Extracts all events and calculates step time of every measure.
	const allStMeasures = rcm.tracks.filter((track) => track.extractedEvents).map((track) => {
		const stMeasures = [];
		let st = 0;
		for (const event of track.extractedEvents) {
			if (event[0] < 0xf5) {
				st += event[1];
			} else if (event[0] === EVENT_RCP.MeasEnd || event[0] === EVENT_RCP.TrackEnd) {
				if (st > 0) {
					stMeasures.push(st);
					st = 0;
				}
			}
		}
		return stMeasures;
	});

	// Chooses the most "common" step times of each measure from all the tracks.
	const maxMeasureNo = Math.max(...allStMeasures.map((e) => e.length));
	const wholeStMeasures = [];
	let survivors = new Set([...new Array(allStMeasures.length)].map((_, i) => i));
	for (let measureNo = 0; measureNo < maxMeasureNo; measureNo++) {
		// Gets each track's step time in the current measure.
		const map = new Map();
		for (let trackNo = 0; trackNo < allStMeasures.length; trackNo++) {
			if (!survivors.has(trackNo)) {
				continue;
			}
			if (measureNo >= allStMeasures[trackNo].length) {
				survivors.delete(trackNo);
				continue;
			}

			const st = allStMeasures[trackNo][measureNo];
			if (map.has(st)) {
				console.assert(Array.isArray(map.get(st)));
				map.get(st).push(trackNo);
			} else {
				map.set(st, [trackNo]);
			}
		}

		if (survivors.size === 0) {
			break;
		}

		// Chooses this measure's step time by "majority vote".
		const entries = [...map.entries()];
		const matchNum = Math.max(...entries.map(([_, trackNos]) => trackNos.length));
		const [st, trackNos] = entries.find(([_, trackNos]) => trackNos.length === matchNum);
		wholeStMeasures.push(st);
		survivors = new Set(trackNos);
	}

	return wholeStMeasures;
}

export function convertRcmToSeq(rcm, options) {
	// Checks the arguments.
	if (!rcm) {
		throw new Error(`Invalid argument: ${rcm}`);
	}

	// Makes a settings object from the default settings and the specified ones.
	const settings = {...defaultSettings, ...options};
	const bitsTable = {none: 0b00, left: 0b01, right: 0b10, both: 0b11};

	// Checks the settings.
	if (Object.keys(settings).filter((e) => /^trim/u.test(e)).some((e) => !Object.keys(bitsTable).includes(settings[e])) ||
	    Object.keys(settings).filter((e) => e in defaultSettings).some((e) => typeof settings[e] !== typeof defaultSettings[e]) ||
	    !['auto', 'signed', 'unsigned'].includes(settings.stPlus)) {
		throw new Error(`Invalid settings: ${settings}`);
	}

	// Makes functions from the settings.
	const setMetaTrackName   =                                     (track, timestamp, bytes) => setEvent(track, timestamp, makeMetaText(0x03, rawTrim(bytes, bitsTable[settings.trimTrackName])));
	const setMetaTextMemo    = (!settings.metaTextMemo)    ? nop : (track, timestamp, bytes) => setEvent(track, timestamp, makeMetaText(0x01, rawTrim(bytes, bitsTable[settings.trimTextMemo])));
	const setMetaTextComment = (!settings.metaTextComment) ? nop : (track, timestamp, bytes) => setEvent(track, timestamp, makeMetaText(0x01, rawTrim(bytes, bitsTable[settings.trimTextComment])));
	const setMetaTextUsrExc  = (!settings.metaTextUsrExc)  ? nop : (track, timestamp, bytes) => setEvent(track, timestamp, makeMetaText(0x01, rawTrim(bytes, bitsTable[settings.trimTextUsrExc])));
	const setMetaCue         = (!settings.metaCue)         ? nop : (track, timestamp, bytes) => setEvent(track, timestamp, makeMetaText(0x07, bytes));

	const makeNoteOff = (settings.noteOff) ? (chNo, noteNo) => makeMidiEvent(0x8, chNo, noteNo, settings.noteOffVel) : (chNo, noteNo) => makeMidiEvent(0x9, chNo, noteNo, 0);

	const validateRange = (settings.ignoreOutOfRange) ? (isValid, message) => validateAndIgnore(isValid, message) : (isValid, message) => validateAndThrow(isValid, message);
	const throwOrIgnore = (settings.ignoreWrongEvent) ? (message) => validateAndIgnore(false, message) : (message) => validateAndThrow(false, message);

	// SMF-related variables
	let startTime = 0;
	const seq = {
		timeBase: rcm.header.timeBase,
		tracks: [],
	};
	const usecPerBeat = 60 * 1000 * 1000 / rcm.header.tempo;

	// Adds a conductor track.
	const conductorTrack = new Map();
	seq.tracks.push(conductorTrack);

	// Sequence Name and Text Events
	setMetaTrackName(conductorTrack, 0, rcm.header.title);
	if (rcm.header.memoLines && rcm.header.memoLines.some((e) => rawTrim(e).length > 0)) {
		for (const memoLine of rcm.header.memoLines) {
			setMetaTextMemo(conductorTrack, 0, memoLine);
		}
	}

	// Time Signature
	const initialBeat = {numer: 4, denom: 4};
	if (rcm.header.beatD !== 0 && (rcm.header.beatD & (rcm.header.beatD - 1) === 0)) {
		initialBeat.numer = rcm.header.beatN;
		initialBeat.denom = rcm.header.beatD;
	}
	setEvent(conductorTrack, 0, makeMetaTimeSignature(initialBeat.numer, initialBeat.denom));

	// Key Signature
	if ('key' in rcm.header) {
		setEvent(conductorTrack, 0, convertKeySignature(rcm.header.key));
	}

	// Adds a setup measure which consists of SysEx converted from control files.
	if (rcm.header.sysExsMTD || rcm.header.sysExsCM6 || rcm.header.sysExsGSD || rcm.header.sysExsGSD2) {
		console.assert(!settings.ignoreCtrlFile);
		const allSysExs = [];

		// Adds SysEx for GS.
		if (rcm.header.sysExsGSD || rcm.header.sysExsGSD2) {
			// Inserts GS reset SysEx.
			if (settings.resetBeforeCtrl) {
				allSysExs.push([0xf0, 0x41, 0x10, 0x42, 0x12, 0x40, 0x00, 0x7f, 0x00, 0x41, 0xf7]);
			}
		}
		if (rcm.header.sysExsGSD) {
			// Adds SysEx from GSD file.
			allSysExs.push(...rcm.header.sysExsGSD);
		}
		if (rcm.header.sysExsGSD2) {
			// Adds SysEx from GSD2 file.
			// TODO: Support >16ch
			allSysExs.push(...rcm.header.sysExsGSD2);
		}

		// Adds SysEx for MT-32/CM-64.
		if (rcm.header.sysExsMTD || rcm.header.sysExsCM6) {
			// Inserts a reset SysEx.
			if (settings.resetBeforeCtrl) {
				allSysExs.push([0xf0, 0x41, 0x10, 0x16, 0x12, 0x7f, 0x00, 0x00, 0x00, 0x01, 0xf7]);
			}
		}
		if (rcm.header.sysExsMTD) {
			// Removes redundant SysEx. (For User Patch)
			const keys = new Set();
			const newSysExs = rcm.header.sysExsMTD.reduce((p, c) => {
				const key = c.slice(5, 8).map((e) => `${e}`).join(',');
				if (!keys.has(key)) {
					p.push(c);
					keys.add(key);
				}
				return p;
			}, []);
			// Adds SysEx from MTD file.
			allSysExs.push(...newSysExs);
		} else if (rcm.header.sysExsCM6) {
			// Adds SysEx from CM6 file.
			allSysExs.push(...rcm.header.sysExsCM6);
		}

		// Removes unnecessary SysEx.
		const sysExs = (settings.optimizeCtrl) ? allSysExs.filter((e) => !isSysExRedundant(e)) : allSysExs;

		if (sysExs.length > 0) {
			// Decides each interval between SysExs.
			const extraTick = calcSetupMeasureTick(initialBeat.numer, initialBeat.denom, seq.timeBase, sysExs.length);
			const timings = spaceEachSysEx(sysExs, extraTick, seq.timeBase, settings.extraSysexWait);
			const maxUsecPerBeat = Math.max(...timings.map((e) => e.usecPerBeat));

			// Sets tempo slow during sending SysExs if necessary.
			setEvent(conductorTrack, 0, makeMetaTempo((maxUsecPerBeat > usecPerBeat) ? maxUsecPerBeat : usecPerBeat));

			// Adds a new track for SysEx.
			const track = new Map();
			seq.tracks.push(track);
			setMetaTrackName(track, 0, new Uint8Array([...'SysEx from control file'.split('').map((e) => e.charCodeAt(0))]));

			// Inserts SysExs from control files.
			let timestamp = startTime;
			for (const timing of timings) {
				setEvent(track, timestamp, timing.sysEx);
				timestamp += timing.tick;
			}

			// Sets original tempo.
			if (maxUsecPerBeat > usecPerBeat) {
				setEvent(conductorTrack, timestamp, makeMetaTempo(usecPerBeat));
			}

			// Shifts the start time.
			startTime += extraTick;

			// Adds an End of Track event to the SysEx track.
			setEvent(track, startTime, [0xff, 0x2f, 0x00]);

		} else {
			// Set Tempo
			setEvent(conductorTrack, 0, makeMetaTempo(usecPerBeat));
		}

	} else {
		// Set Tempo
		setEvent(conductorTrack, 0, makeMetaTempo(usecPerBeat));
	}

	// Adds Time Signature meta events from each measure's step time.
	if (settings.metaTimeSignature) {
		const stMeasures = getMeasureSt(rcm);
		const maxMeasureSt = Math.max(seq.timeBase * initialBeat.numer * 2 / initialBeat.denom, 192 * 2);
		const maxDenom = 16;
		const minBeatSt = seq.timeBase * 4 / maxDenom;
		if (stMeasures.every((st) => st <= maxMeasureSt) && stMeasures.every((st) => st % minBeatSt === 0)) {
			// Makes each measure's time signature.
			const beats = stMeasures.map((st) => {
				for (let denom = initialBeat.denom; denom <= maxDenom; denom *= 2) {
					const beatSt = seq.timeBase * 4 / denom;
					const numer = st / beatSt;
					if (Number.isInteger(numer)) {
						return {numer, denom};
					}
				}
				console.assert(false);
				return null;
			});
			const dedupedBeats = beats.map((e, i, a) => {
				const p = (i > 0) ? a[i - 1] : initialBeat;
				return (e.numer === p.numer && e.denom === p.denom) ? null : e;
			});

			// Adds Time Signature meta events.
			let timestamp = 0;
			console.assert(stMeasures.length === dedupedBeats.length);
			for (let i = 0; i < stMeasures.length; i++) {
				if (dedupedBeats[i]) {
					setEvent(conductorTrack, startTime + timestamp, makeMetaTimeSignature(dedupedBeats[i].numer, dedupedBeats[i].denom));
				}
				timestamp += stMeasures[i];
			}
		}
	}

	// Converts each track.
	const EVENT = (rcm.header.isMCP) ? EVENT_MCP : EVENT_RCP;
	const isAllPortSame = ((new Set(rcm.tracks.map((e) => e.portNo))).size === 1);
	const isNoteOff = (rcm.header.isMCP) ? ((gt, st) => (gt < st)) : ((gt, st) => (gt <= st));
	let maxDuration = 0;
	const tempoEventMap = new Map();
	for (const rcmTrack of rcm.tracks) {
		// Skips the track if it is empty or muted.
		if (!rcmTrack.extractedEvents || rcmTrack.extractedEvents.length <= 1 || (rcmTrack.mode & 0x01) !== 0) {
			continue;
		}

		const smfTrack = new Map();
		const noteGts = new Array(128).fill(-1);
		const patchNos = [...Array(128).keys()];
		const keyShift = (rcm.header.isMCP || (rcmTrack.keyShift & 0x80) !== 0) ? 0 : rcm.header.playBias + rcmTrack.keyShift - ((rcmTrack.keyShift >= 0x40) ? 0x80 : 0);
		let timestamp = startTime + (rcmTrack.stShift || 0);
		let {chNo, portNo, midiCh} = rcmTrack;
		let rolDev, rolBase, yamDev, yamBase;	// TODO: Investigate whether they belong to track or global.

		// Track name
		setMetaTrackName(smfTrack, 0, rcmTrack.memo);

		// If any port No. are not same among all the track, adds an unofficial MIDI Port meta event. (FF 21 01 pp)
		if (!isAllPortSame) {
			setEvent(smfTrack, 0, [0xff, 0x21, 0x01, portNo]);
		}

		// Converts each RCM event to MIDI/SysEx/meta event.
		for (const event of rcmTrack.extractedEvents) {
			const [cmd, stOrg, gt, vel] = event;
			let st = stOrg;

			if (cmd < 0x80) {
				// Note event
				if (chNo >= 0 && gt > 0 && vel > 0) {
					if (validateRange(isIn7bitRange(vel), `Invalid note-on event: [${hexStr(event)}]`)) {
						const noteNo = cmd + keyShift;
						if (0 <= noteNo && noteNo < 0x80) {
							// Note on or tie
							if (noteGts[noteNo] < 0) {
								setEvent(smfTrack, timestamp, makeMidiEvent(0x9, chNo, noteNo, vel));
							}
							noteGts[noteNo] = gt;
						} else {
							console.warn(`Note No. of note-on event is out of range due to KEY+ and/or PLAY BIAS: (${cmd} -> ${noteNo}) Ignored.`);
						}
					}
				}

			} else {
				// Command event
				switch (cmd) {
				// MIDI messages
				case EVENT.CONTROL:
					if (chNo >= 0) {
						if (validateRange(isIn7bitRange(gt, vel), `Invalid CONTROL event: [${hexStr(event)}]`)) {
							setEvent(smfTrack, timestamp, makeMidiEvent(0xb, chNo, gt, vel));
						}
					}
					break;
				case EVENT.PITCH:
					if (chNo >= 0) {
						if (validateRange(isIn7bitRange(gt, vel), `Invalid PITCH event: [${hexStr(event)}]`)) {
							setEvent(smfTrack, timestamp, makeMidiEvent(0xe, chNo, gt, vel));
						}
					}
					break;
				case EVENT.AFTER_C:
					if (chNo >= 0) {
						if (validateRange(isIn7bitRange(gt), `Invalid AFTER C. event: [${hexStr(event)}]`)) {
							setEvent(smfTrack, timestamp, makeMidiEvent(0xd, chNo, gt));
						}
					}
					break;
				case EVENT.AFTER_K:
					if (chNo >= 0) {
						if (validateRange(isIn7bitRange(gt, vel), `Invalid AFTER K. event: [${hexStr(event)}]`)) {
							setEvent(smfTrack, timestamp, makeMidiEvent(0xa, chNo, gt, vel));
						}
					}
					break;
				case EVENT.PROGRAM:
					if (chNo >= 0) {
						if (validateRange(isIn7bitRange(gt), `Invalid PROGRAM event: [${hexStr(event)}]`)) {
							setEvent(smfTrack, timestamp, makeMidiEvent(0xc, chNo, gt));
						}
					}
					break;
				case EVENT.BankPrgL:
				case EVENT.BankPrg:
					if (chNo >= 0) {
						if (validateRange(isIn7bitRange(gt, vel), `Invalid BankPrg event: [${hexStr(event)}]`)) {
							// Note: According to the MIDI spec, Bank Select must be transmitted as a pair of MSB and LSB.
							// But, a BankPrg event is converted to a single MSB or LSB at the current implementation.
							setEvent(smfTrack, timestamp, makeMidiEvent(0xb, chNo, (cmd === EVENT.BankPrg) ? 0 : 32, vel));
							setEvent(smfTrack, timestamp, makeMidiEvent(0xc, chNo, gt));
						}
					}
					break;
				case EVENT.UserPrg:
					if (chNo >= 0) {
						if (validateRange((0 <= gt && gt < 192), `Invalid PROGRAM (User Program) event: [${hexStr(event)}]`)) {
							// Inserts a SysEx to set Patch Memory if necessary.
							const progNo = gt & 0x7f;
							if (patchNos[progNo] !== gt && rcm.header.patches) {
								const addr = progNo * 8;
								const bytes = [0x41, 0x10, 0x16, 0x12, 0x83, 0x05, (addr >> 7) & 0x7f, addr & 0x7f, ...rcm.header.patches[gt], 0x84];
								console.assert(bytes.length === 17);
								setEvent(smfTrack, timestamp, convertSysEx(bytes, 0, 0, 0));
								patchNos[progNo] = gt;
							}

							setEvent(smfTrack, timestamp, [0xc0 | chNo, progNo]);
						}
					}
					break;

				// SysEx
				case EVENT.UsrExc0:
				case EVENT.UsrExc1:
				case EVENT.UsrExc2:
				case EVENT.UsrExc3:
				case EVENT.UsrExc4:
				case EVENT.UsrExc5:
				case EVENT.UsrExc6:
				case EVENT.UsrExc7:
					if (validateRange(isIn7bitRange(gt, vel), `Invalid UsrExc event: [${hexStr(event)}]`)) {
						const index = cmd - EVENT.UsrExc0;
						const {bytes, memo} = rcm.header.userSysExs[index];
						const sysEx = convertSysEx(bytes, (isAllPortSame) ? chNo : midiCh, gt, vel);
						if (validateRange(sysEx && isIn7bitRange(sysEx.slice(1, -1)), `Invalid definition of UsrExc${index}: [${hexStr(bytes)}]`)) {
							setMetaTextUsrExc(smfTrack, timestamp, memo);
							setEvent(smfTrack, timestamp, sysEx);
						}
					}
					break;
				case EVENT.TrExcl:
					if (validateRange(isIn7bitRange(gt, vel), `Invalid Tr.Excl event: [${hexStr(event)}]`)) {
						const bytes = event.slice(4);
						if (bytes.length > 0) {
							const sysEx = convertSysEx(bytes, (isAllPortSame) ? chNo : midiCh, gt, vel);
							if (validateRange(sysEx && isIn7bitRange(sysEx.slice(1, -1)), `Invalid definition of Tr.Excl: [${hexStr(bytes)}]`)) {
								setEvent(smfTrack, timestamp, sysEx);
							}
						}
					}
					break;

				// 1-byte DT1 SysEx for Roland devices
				case EVENT.RolBase:
					if (validateRange(isIn7bitRange(gt, vel), `Invalid RolBase event: [${hexStr(event)}]`)) {
						rolBase = [gt, vel];
					}
					break;
				case EVENT.RolDev:
					if (validateRange(isIn7bitRange(gt, vel), `Invalid RolDev# event: [${hexStr(event)}]`)) {
						rolDev = [gt, vel];
					}
					break;
				case EVENT.RolPara:
					if (validateRange(isIn7bitRange(gt, vel), `Invalid RolPara event: [${hexStr(event)}]`)) {
						// Initializes RolDev# and RolBase if they have not been set yet.
						if (!rolDev) {
							rolDev = [settings.rolandDevId, settings.rolandModelId];
							console.warn(`RolDev# has not been set yet. Initialized to [${hexStr(rolDev)}].`);
						}
						if (!rolBase) {
							rolBase = [settings.rolandBaseAddrH, settings.rolandBaseAddrM];
							console.warn(`RolBase has not been set yet. Initialized to [${hexStr(rolBase)}].`);
						}
						// Makes a SysEx by UsrExcl/Tr.Excl parser.
						const bytes = [0x41, ...rolDev, 0x12, 0x83, ...rolBase, 0x80, 0x81, 0x84];
						console.assert(bytes.length === 10);
						setEvent(smfTrack, timestamp, convertSysEx(bytes, 0, gt, vel));
					}
					break;

				// 1-byte parameter change SysEx for Yamaha XG devices
				case EVENT.YamBase:
					if (validateRange(isIn7bitRange(gt, vel), `Invalid YamBase event: [${hexStr(event)}]`)) {
						yamBase = [gt, vel];
					}
					break;
				case EVENT.YamDev:
					if (validateRange(isIn7bitRange(gt, vel), `Invalid YamDev# event: [${hexStr(event)}]`)) {
						yamDev = [gt, vel];
					}
					break;
				case EVENT.YamPara:
					if (validateRange(isIn7bitRange(gt, vel), `Invalid YamPara event: [${hexStr(event)}]`)) {
						// Initializes YamDev# and YamBase if they have not been set yet.
						if (!yamDev) {
							yamDev = [settings.yamahaDevId, settings.yamahaModelId];
							console.warn(`YamDev# has not been set yet. Initialized to [${hexStr(yamDev)}].`);
						}
						if (!yamBase) {
							yamBase = [settings.yamahaBaseAddrH, settings.yamahaBaseAddrM];
							console.warn(`YamBase has not been set yet. Initialized to [${hexStr(yamBase)}].`);
						}
						// Makes a SysEx by UsrExcl/Tr.Excl parser.
						const bytes = [0x43, ...yamDev, 0x83, ...yamBase, 0x80, 0x81, 0x84];
						console.assert(bytes.length === 9);
						setEvent(smfTrack, timestamp, convertSysEx(bytes, 0, gt, vel));
					}
					break;
				case EVENT.XGPara:
					if (validateRange(isIn7bitRange(gt, vel), `Invalid XGPara event: [${hexStr(event)}]`)) {
						// Initializes YamDev# and YamBase if they have not been set yet.
						if (!yamDev) {
							yamDev = [settings.yamahaDevId, settings.yamahaModelId];
							console.warn(`YamDev# has not been set yet. Initialized to [${hexStr(yamDev)}].`);
						}
						if (!yamBase) {
							yamBase = [settings.yamahaBaseAddrH, settings.yamahaBaseAddrM];
							console.warn(`YamBase has not been set yet. Initialized to [${hexStr(yamBase)}].`);
						}
						// Makes a SysEx.
						const bytes = [0xf0, 0x43, ...yamDev, ...yamBase, gt, vel, 0xf7];
						console.assert(bytes.length === 9);
						setEvent(smfTrack, timestamp, bytes);
					}
					break;

				// Meta events
				case EVENT.MIDI_CH:
					if (validateRange((0 <= gt && gt <= 32), `Invalid MIDI CH. event: [${hexStr(event)}]`)) {
						const oldPortNo = portNo;
						midiCh = gt - 1;	// The internal representations of MIDI CH. are different between track headers and event.
						chNo   = (midiCh >= 0) ? midiCh % 16 : -1;
						portNo = (midiCh >= 0) ? Math.trunc(midiCh / 16) : portNo;

						// Adds an unofficial MIDI Port meta event if necessary.
						if (portNo !== oldPortNo) {
							// TODO: Investigate whether this event can be appeared in the song body.
							setEvent(smfTrack, timestamp, [0xff, 0x21, 0x01, portNo]);
						}
					}
					break;

				case EVENT.TEMPO:
					if (validateRange((gt > 0), `Invalid tempo rate: ${gt}`)) {	// Note: It can be greater than 255 in G36.
						tempoEventMap.set(timestamp, event);
					}
					break;

				case EVENT.MusicKey:
					setEvent(conductorTrack, timestamp, convertKeySignature(stOrg));
					st = 0;
					break;

				case EVENT.Comment:
					setMetaTextComment(smfTrack, timestamp, event.slice(1));
					st = 0;
					break;

				case EVENT.ExtCmd:
					{
						const kind = (gt === 0x00) ? 'MCI: ' : (gt === 0x01) ? 'RUN: ' : '???: ';
						setMetaCue(conductorTrack, timestamp, [...strToBytes(kind), ...event.slice(4)]);
					}
					break;

				case EVENT.KeyScan:
					{
						const cue = {
							12: 'Suspend playing',
							18: 'Increase play bias',
							23: 'Stop playing',
							32: 'Show main screen',
							33: 'Show 11th track',
							34: 'Show 12th track',
							35: 'Show 13th track',
							36: 'Show 14th track',
							37: 'Show 15th track',
							38: 'Show 16th track',
							39: 'Show 17th track',
							40: 'Show 18th track',
							48: 'Show 10th track',
							49: 'Show 1st track',
							50: 'Show 2nd track',
							51: 'Show 3rd track',
							52: 'Show 4th track',
							53: 'Show 5th track',
							54: 'Show 6th track',
							55: 'Show 7th track',
							56: 'Show 8th track',
							57: 'Show 9th track',
							61: 'Mute 1st track',
						}[gt] || 'Unknown';
						setMetaCue(conductorTrack, timestamp, [...strToBytes(`KeyScan: ${cue}`)]);
					}
					break;

				// RCM commands
				case EVENT.MeasEnd:
					st = 0;
					break;
				case EVENT.TrackEnd:
					// Expands the current step time to wait for all of note-off.
					st = Math.max(...noteGts, 0);
					break;

				case EVENT.SecondEvt:
				case EVENT.LoopEnd:
				case EVENT.LoopStart:
				case EVENT.SameMeas:
					console.assert(false, 'Such kind of events must be resolved in the previous phase', {event});
					throwOrIgnore(`Unexpected event: [${hexStr(event)}]`);
					break;

				// Special commands for particular devices
				case EVENT.DX7FUNC:
				case EVENT.DX_PARA:
				case EVENT.DX_PERF:
				case EVENT.TX_FUNC:
				case EVENT.FB_01_P:
				case EVENT.FB_01_S:
				case EVENT.TX81Z_V:
				case EVENT.TX81Z_A:
				case EVENT.TX81Z_P:
				case EVENT.TX81Z_S:
				case EVENT.TX81Z_E:
				case EVENT.DX7_2_R:
				case EVENT.DX7_2_A:
				case EVENT.DX7_2_P:
				case EVENT.TX802_P:
				case EVENT.MKS_7:
					if (chNo >= 0) {
						const eventName = Object.entries(EVENT).find((e) => e[1] === cmd)[0];
						console.assert(eventName);
						if (validateRange(isIn7bitRange(gt, vel), `Invalid ${eventName} event: [${hexStr(event)}]`)) {
							const bytes = {
								DX7FUNC: [0xf0, 0x43, 0x10 | chNo, 0x08, gt, vel, 0xf7],
								DX_PARA: [0xf0, 0x43, 0x10 | chNo, 0x00, gt, vel, 0xf7],
								DX_PERF: [0xf0, 0x43, 0x10 | chNo, 0x04, gt, vel, 0xf7],
								TX_FUNC: [0xf0, 0x43, 0x10 | chNo, 0x11, gt, vel, 0xf7],
								FB_01_P: [0xf0, 0x43, 0x10 | chNo, 0x15, gt, vel, 0xf7],
								FB_01_S: [0xf0, 0x43, 0x75, chNo, 0x10, gt, vel, 0xf7],
								TX81Z_V: [0xf0, 0x43, 0x10 | chNo, 0x12, gt, vel, 0xf7],
								TX81Z_A: [0xf0, 0x43, 0x10 | chNo, 0x13, gt, vel, 0xf7],
								TX81Z_P: [0xf0, 0x43, 0x10 | chNo, 0x10, gt, vel, 0xf7],
								TX81Z_S: [0xf0, 0x43, 0x10 | chNo, 0x10, 0x7b, gt, vel, 0xf7],
								TX81Z_E: [0xf0, 0x43, 0x10 | chNo, 0x10, 0x7c, gt, vel, 0xf7],
								DX7_2_R: [0xf0, 0x43, 0x10 | chNo, 0x1b, gt, vel, 0xf7],
								DX7_2_A: [0xf0, 0x43, 0x10 | chNo, 0x18, gt, vel, 0xf7],
								DX7_2_P: [0xf0, 0x43, 0x10 | chNo, 0x19, gt, vel, 0xf7],
								TX802_P: [0xf0, 0x43, 0x10 | chNo, 0x1a, gt, vel, 0xf7],
								MKS_7:   [0xf0, 0x41, 0x32, chNo, gt, vel, 0xf7],
							}[eventName];
							console.assert(Array.isArray(bytes));
							setEvent(smfTrack, timestamp, bytes);
						}
					}
					break;
				case EVENT.CMU_800:
					console.warn(`CMU-800 is not supported: ${gt}`);
					break;

				default:
					throwOrIgnore(`Unknown event: [${hexStr(event)}]`);
					st = 0;
					break;
				}
			}

			// Note off
			if (chNo >= 0) {
				for (let noteNo = 0; noteNo < noteGts.length; noteNo++) {
					const noteGt = noteGts[noteNo];
					if (noteGt < 0) {
						continue;
					}

					if (isNoteOff(noteGt, st)) {
						setEvent(smfTrack, timestamp + noteGt, makeNoteOff(chNo, noteNo));
						noteGts[noteNo] = -1;
					} else {
						noteGts[noteNo] -= st;
					}
				}
			}

			timestamp += st;
		}

		// End of Track
		setEvent(smfTrack, timestamp, [0xff, 0x2f, 0x00]);
		if (timestamp > maxDuration) {
			maxDuration = timestamp;
		}

		seq.tracks.push(smfTrack);
	}

	// End of Track for the conductor track
	setEvent(conductorTrack, maxDuration, [0xff, 0x2f, 0x00]);

	// Makes tempo meta events.
	addTempoEvents(tempoEventMap);

	return seq;

	// Note: The process of the tempo graduation is different from the original Recomposer's algorithm.
	function addTempoEvents(tempoEventMap) {
		// Table of step time during graduation from CVS.EXE Ver 5.06 (1995-08-29) [0x00dcd8-0x00ddd7]
		const gradSteps = [
			NaN, 255, 225, 208, 195, 186, 178, 171, 165, 160, 156, 151, 148, 144, 141, 138,
			135, 132, 130, 128, 125, 123, 121, 119, 117, 116, 114, 112, 111, 109, 108, 106,
			105, 104, 102, 101, 100,  99,  98,  96,  95,  94,  93,  92,  91,  90,  89,  88,
			 87,  86,  86,  85,  84,  83,  82,  81,  81,  80,  79,  78,  78,  77,  76,  76,
			 75,  74,  74,  73,  72,  72,  71,  70,  70,  69,  69,  68,  67,  67,  66,  66,
			 65,  65,  64,  64,  63,  63,  62,  62,  61,  61,  60,  60,  59,  59,  58,  58,
			 57,  57,  56,  56,  56,  55,  55,  54,  54,  53,  53,  53,  52,  52,  51,  51,
			 51,  50,  50,  49,  49,  49,  48,  48,  48,  47,  47,  47,  46,  46,  45,  45,
			 45,  44,  44,  44,  43,  43,  43,  42,  42,  42,  42,  41,  41,  41,  40,  40,
			 40,  39,  39,  39,  38,  38,  38,  38,  37,  37,  37,  36,  36,  36,  36,  35,
			 35,  35,  35,  34,  34,  34,  33,  33,  33,  33,  32,  32,  32,  32,  31,  31,
			 31,  31,  30,  30,  30,  30,  29,  29,  29,  29,  29,  28,  28,  28,  28,  27,
			 27,  27,  27,  26,  26,  26,  26,  26,  25,  25,  25,  25,  25,  24,  24,  24,
			 24,  23,  23,  23,  23,  23,  22,  22,  22,  22,  22,  21,  21,  21,  21,  21,
			 20,  20,  20,  20,  20,  20,  19,  19,  19,  19,  19,  18,  18,  18,  18,  18,
			 17,  17,  17,  17,  17,  17,  16,  16,  16,  16,  16,  16,  15,  15,  15,  15,
		];

		let currentTempo = rcm.header.tempo;
		let gradTempoMap = null;
		for (let timestamp = 0; timestamp < maxDuration; timestamp++) {
			const oldTempo = currentTempo;

			// Checks if a tempo event exists.
			if (tempoEventMap.has(timestamp)) {
				const [cmd, _, gt, vel] = tempoEventMap.get(timestamp);
				console.assert(cmd === EVENT.TEMPO);

				if (vel === 0) {	// Normal tempo change
					gradTempoMap = null;	// Cancels tempo graduation.
					currentTempo = Math.trunc(rcm.header.tempo * gt / 64.0);

				} else {	// Tempo change with graduation
					const targetTempo = Math.trunc(rcm.header.tempo * gt / 64.0);
					const gradSt = gradSteps[vel];

					// Calculates future tempo values.
					gradTempoMap = new Map();
					for (let i = 0; i < gradSt; i += 2) {
						const gradTimestamp = timestamp + Math.trunc(i * rcm.header.timeBase / 48.0);
						const gradTempo = Math.trunc(currentTempo + (targetTempo - currentTempo) * i / gradSt);
						gradTempoMap.set(gradTimestamp, gradTempo);
					}
					gradTempoMap.set(timestamp + Math.trunc(gradSt * rcm.header.timeBase / 48.0), targetTempo);
				}
			}

			// If in the "Tempo graduation", updates the current tempo with the pre-calculated tempo values.
			if (gradTempoMap) {
				if (gradTempoMap.has(timestamp)) {
					currentTempo = gradTempoMap.get(timestamp);
				}
			}

			// Adds tempo meta event if necessary.
			if (currentTempo !== oldTempo) {
				setEvent(conductorTrack, timestamp, makeMetaTempo(60 * 1000 * 1000 / currentTempo));
			}
		}
	}

	function setEvent(map, timestamp, bytes) {
		console.assert(map instanceof Map, 'Invalid argument', {map});
		console.assert(Number.isInteger(timestamp), 'Invalid argument', {timestamp});
		console.assert(bytes && bytes.length, 'Invalid argument', {bytes});

		if (timestamp < 0) {
			console.warn(`An event appeared previous to the zero point due to ST+. Adjusted it to zero: (${timestamp} -> 0)`);
			timestamp = 0;
		}
		if (!map.has(timestamp)) {
			map.set(timestamp, []);
		}
		map.get(timestamp).push(bytes);
	}

	function convertSysEx(bytes, ch, gt, vel) {
		console.assert(bytes && bytes.length, 'Invalid argument', {bytes});

		const sysEx = [0xf0];
		let checkSum = 0;
		loop: for (const byte of bytes) {
			let value = byte;
			switch (byte) {
			case 0x80:	// [gt]
				value = gt;
				break;
			case 0x81:	// [ve]
				value = vel;
				break;
			case 0x82:	// [ch]
				if (ch < 0) {
					return null;
				}
				value = ch;
				break;
			case 0x83:	// [cs]
				checkSum = 0;
				continue;
			case 0x84:	// [ss]
				value = (0x80 - checkSum) & 0x7f;
				break;
			case 0xf7:
				break loop;
			default:
				break;
			}

			if (!isIn7bitRange(value)) {
				return null;
			}

			// Adds a value and updates the checksum.
			sysEx.push(value);
			checkSum = (checkSum + value) & 0x7f;
		}

		// Adds trailing 0xf7.
		console.assert(sysEx[sysEx.length - 1] !== 0xf7);
		sysEx.push(0xf7);

		return sysEx;
	}

	function convertKeySignature(value) {
		console.assert(Number.isInteger(value), 'Invalid argument', {value});
		const tmp = value & 0x0f;
		const sf = (tmp < 8) ? tmp : 8 - tmp;
		console.assert(-7 <= sf && sf <= 7);
		const mi = ((value & 0x10) === 0) ? 0x00 : 0x01;
		return [0xff, 0x59, 0x02, (sf + 0x100) & 0xff, mi];
	}

	function makeMidiEvent(kind, ch, ...values) {
		console.assert((0x8 <= kind && kind <= 0xe), 'Invalid argument', {kind});
		console.assert((0 <= ch && ch < 16), 'Invalid argument', {ch});
		console.assert(values && values.length === [2, 2, 2, 2, 1, 1, 2][kind - 0x8], 'Invalid argument', {values});
		console.assert(values.some((e) => Number.isInteger(e) && (e & ~0x7f) === 0), 'Invalid argument', {values});
		return [(kind << 4) | ch, ...values];
	}

	function makeMetaText(kind, bytes) {
		console.assert((0x01 <= kind && kind <= 0x0f), 'Invalid argument', {kind});
		console.assert(bytes && 'length' in bytes, 'Invalid argument', {bytes});
		return [0xff, kind, ...varNum(bytes.length), ...bytes];
	}

	function makeMetaTempo(usecPerBeat) {
		console.assert(Number.isFinite(usecPerBeat), 'Invalid argument', {usecPerBeat});
		const bytes = new Uint8Array(4);
		(new DataView(bytes.buffer)).setUint32(0, Math.trunc(usecPerBeat));
		return [0xff, 0x51, 0x03, ...bytes.slice(1)];
	}

	function makeMetaTimeSignature(numer, denom) {
		console.assert(Number.isInteger(numer), 'Invalid argument', {numer});
		console.assert(Number.isInteger(denom) && (denom & (denom - 1)) === 0, 'Invalid argument', {denom});
		return [0xff, 0x58, 0x04, numer, Math.log2(denom), 0x18, 0x08];
	}
}

export function convertSeqToSmf(seq) {
	console.assert(seq, 'Invalid argument', {seq});

	// Makes a header chunk.
	const mthd = [
		...strToBytes('MThd'),
		...uintBE(2 + 2 + 2, 4),
		...uintBE(1, 2),
		...uintBE(seq.tracks.length, 2),
		...uintBE(seq.timeBase, 2),
	];

	// Makes track chunks.
	const mtrks = seq.tracks.map((smfTrack) => {
		let prevTime = 0;
		let lastStatus = 0;
		const mtrk = [...smfTrack.entries()].sort((a, b) => a[0] - b[0]).reduce((p, c) => {
			const [timestamp, events] = c;

			// Makes MTrk events.
			const bytes = [];
			for (const event of events) {
				// Delta time
				const deltaTime = timestamp - prevTime;
				bytes.push(...varNum(deltaTime));
				prevTime = timestamp;

				// Event
				const status = event[0];
				if (status < 0xf0) {
					// Channel messages
					console.assert(status >= 0x80);
					if (status === lastStatus) {
						// Applies running status rule.
						bytes.push(...event.slice(1));
					} else {
						bytes.push(...event);
					}
					lastStatus = status;

				} else if (status === 0xf0) {
					// SysEx
					bytes.push(0xf0, ...varNum(event.length - 1), ...event.slice(1));
					lastStatus = 0;

				} else {
					// Meta events
					console.assert(status === 0xff);	// This converter doesn't generate F7 SysEx.
					bytes.push(...event);
					lastStatus = 0;
				}
			}

			p.push(...bytes);
			return p;
		}, []);

		// Extracts MTrk events with a leading MTrk header.
		return [...strToBytes('MTrk'), ...uintBE(mtrk.length, 4), ...mtrk];
	});

	// Extracts track events with a leading header chunk.
	const smf = mthd.concat(...mtrks);

	return new Uint8Array(smf);

	function uintBE(value, width) {
		console.assert(Number.isInteger(value) && (width === 2 || width === 4), 'Invalid argument', {value, width});
		const bytes = [];
		for (let i = 0; i < width; i++) {
			bytes.unshift(value & 0xff);
			value >>= 8;
		}
		console.assert(value === 0);
		return bytes;
	}
}

function varNum(value) {
	console.assert(Number.isInteger(value) && (0 <= value && value < 0x10000000), 'Invalid argument', {value});
	if (value < 0x80) {
		return [value];
	} else if (value < 0x4000) {
		return [(value >> 7) | 0x80, value & 0x7f];
	} else if (value < 0x200000) {
		return [(value >> 14) | 0x80, ((value >> 7) & 0x7f) | 0x80, value & 0x7f];
	} else {
		return [(value >> 21) | 0x80, ((value >> 14) & 0x7f) | 0x80, ((value >> 7) & 0x7f) | 0x80, value & 0x7f];
	}
}

function hexStr(bytes) {
	console.assert(bytes && 'length' in bytes, 'Invalid argument', {bytes});
	return [...bytes].map((e) => e.toString(16).padStart(2, '0')).join(' ');
}

function strToBytes(str) {
	console.assert(typeof str === 'string' && /^[\x20-\x7E]*$/u.test(str), 'Invalid argument', {str});
	return str.split('').map((e) => e.codePointAt(0));
}

function rawTrim(bytes, bits = 0b11) {
	console.assert(bytes && 'length' in bytes, 'Invalid argument', {bytes});
	console.assert(Number.isInteger(bits) && (bits & ~0b11) === 0, 'Invalid argument', {bits});

	if (bytes.every((e) => e === 0x20)) {
		return new Uint8Array();
	}

	const begin = ((bits & 0b01) === 0) ? 0         : bytes.findIndex((e) => e !== 0x20);
	const end   = ((bits & 0b10) === 0) ? undefined : String.fromCharCode(...bytes).replace(/\x20+$/u, '').length;

	return bytes.slice(begin, end);
}

function rawTrimNul(bytes) {
	console.assert(bytes && 'length' in bytes, 'Invalid argument', {bytes});

	const index = bytes.indexOf(0x00);
	if (index < 0) {
		return bytes;
	} else {
		return bytes.slice(0, index);
	}
}

function isIn7bitRange(...values) {
	console.assert(values && values.length, 'Invalid argument', {values});
	return values.every((e) => (e & ~0x7f) === 0);
}

function validateAndThrow(isValid, message) {
	if (!isValid) {
		throw new Error(message);
	}
	return true;
}

function validateAndIgnore(isValid, message) {
	if (!isValid) {
		console.warn(`${message} Ignored.`);
	}
	return isValid;
}

function nop() {
	/* EMPTY */
}
