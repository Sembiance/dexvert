import {Format} from "../../Format.js";

export class windowsSCR extends Format
{
	name           = "Windows Screensaver";
	ext            = [".scr"];
	forbidExtMatch = true;
	magic          = ["Windows New Executable", "MS-DOS executable, NE for MS Windows 3.x", "Win16 NE executable", "Windows screen saver"];
	weakMagic      = true;

	converters = ["deark"];
}

/*
TODO
exports.inputMeta = (state0, p0, cb) => p0.util.flow.serial([
	() => ({program : "winedump"}),
	(state, p) =>
	{
		const winedumpMeta = p.util.program.getMeta(state, "winedump");
		if(winedumpMeta)
			state.input.meta[p.format.meta.formatid] = winedumpMeta;
		
		return p.util.flow.noop;
	}
])(state0, p0, cb);
*/
