import {xu} from "xu";
import {cmdUtil} from "xutil";
import {UInt8ArrayReader} from "UInt8ArrayReader";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Converts <input.bas> from tokenized STOS BAS to <output.txt>",
	args :
	[
		{argid : "inputFilePath", desc : "STOS BAS file path to convert", required : true},
		{argid : "outputFilePath", desc : "Output file to write to", required : true}
	]});


/* eslint-disable max-len, unicorn/number-literal-case */
const MAIN = {0X80 : "to", 0X81 : "step", 0X82 : "next", 0X83 : "wend", 0X84 : "until", 0X85 : "dim", 0X86 : "poke", 0X87 : "doke", 0X88 : "loke", 0X89 : "read", 0X8A : "rem", 0X8B : "return", 0X8C : "pop", 0X8D : "resume next", 0X8E : "resume", 0X8F : "on error", 0X90 : "screen copy", 0X91 : "swap", 0X92 : "plot", 0X93 : "pie", 0X94 : "draw", 0X95 : "polyline", 0X96 : "polymark", 0X98 : "goto", 0X99 : "gosub", 0X9A : "then", 0X9B : "else", 0X9C : "restore", 0X9D : "for", 0X9E : "while", 0X9F : "repeat", 0XA1 : "print", 0XA2 : "if", 0XA3 : "update", 0XA4 : "sprite", 0XA5 : "freeze", 0XA6 : "off", 0XA7 : "on", 0XA9 : "locate", 0XAA : "paper", 0XAB : "pen", 0XAC : "home", 0XAD : ".b", 0XAE : ".w", 0XAF : ".l", 0XB0 : "cup", 0XB1 : "cdown", 0XB2 : "cleft", 0XB3 : "cright", 0XB4 : "cls", 0XB5 : "inc", 0XB6 : "dec", 0XB7 : "screen swap", 0XB9 : "psg", 0XBA : "scrn", 0XBB : "dreg", 0XBC : "areg", 0XBD : "point", 0XBE : "drive$", 0XBF : "dir$", 0XC1 : "abs", 0XC2 : "colour", 0XC3 : "fkey", 0XC4 : "sin", 0XC5 : "cos", 0XC6 : "drive", 0XC7 : "timer", 0XC8 : "logic", 0XC9 : "fn", 0XCA : "not", 0XCB : "rnd", 0XCC : "val", 0XCD : "asc", 0XCE : "chr$", 0XCF : "inkey$", 0XD0 : "scancode", 0XD1 : "mid$", 0XD2 : "right$", 0XD3 : "left$", 0XD4 : "length", 0XD5 : "start", 0XD6 : "len", 0XD7 : "pi", 0XD8 : "peek", 0XD9 : "deek", 0XDA : "leek", 0XDB : "zone", 0XDC : "x sprite", 0XDD : "y sprite", 0XDE : "x mouse", 0XDF : "y mouse", 0XE0 : "mouse key", 0XE1 : "physic", 0XE2 : "back", 0XE3 : "log", 0XE4 : "pof", 0XE5 : "mode", 0XE6 : "time$", 0XE7 : "date$", 0XE8 : "screen$", 0XE9 : "default", 0XEB : "xor", 0XEC : "or", 0XED : "and", 0XEE : "<>", 0XEF : "<=", 0XF0 : ">=", 0XF1 : "=", 0XF2 : "<", 0XF3 : ">", 0XF4 : "+", 0XF5 : "-", 0XF6 : "mod", 0XF7 : "*", 0XF8 : "/", 0XF9 : "^"};
const EXTENDED_INSTRUCTIONS = {0X00 : "listbank", 0X01 : "llistbank", 0X02 : "follow", 0X03 : "frequency", 0X04 : "cont", 0X05 : "change", 0X06 : "search", 0X07 : "delete", 0X08 : "merge", 0X09 : "auto", 0X0A : "new", 0X0B : "unnew", 0X0C : "fload", 0X0D : "fsave", 0X0E : "reset", 0X0F : "system", 0X10 : "env", 0X11 : "renum", 0X12 : "multi", 0X13 : "full", 0X14 : "grab", 0X15 : "list", 0X16 : "llist", 0X17 : "hexa", 0X19 : "accload", 0X1A : "accnew", 0X1B : "lower", 0X1C : "upper", 0X1D : "english", 0X1E : "francais", 0X70 : "dir/w", 0X71 : "fade", 0X72 : "bcopy", 0X73 : "square", 0X74 : "previous", 0X75 : "transpose", 0X76 : "shift", 0X77 : "wait key", 0X78 : "dir", 0X79 : "ldir", 0X7A : "bload", 0X7B : "bsave", 0X7C : "qwindow", 0X7D : "as set", 0X7E : "charcopy", 0X7F : "under", 0X80 : "menu$", 0X81 : "menu", 0X82 : "title", 0X83 : "border", 0X84 : "hardcopy", 0X85 : "windcopy", 0X86 : "redraw", 0X87 : "centre", 0X88 : "tempo", 0X89 : "volume", 0X8A : "envel", 0X8B : "boom", 0X8C : "shoot", 0X8D : "bell", 0X8E : "play", 0X8F : "noise", 0X90 : "voice", 0X91 : "music", 0X92 : "box", 0X93 : "rbox", 0X94 : "bar", 0X95 : "rbar", 0X96 : "appear", 0X97 : "bclr", 0X98 : "bset", 0X99 : "rol", 0X9A : "ror", 0X9B : "curs", 0X9C : "clw", 0X9D : "bchg", 0X9E : "call", 0X9F : "trap", 0XA1 : "run", 0XA2 : "clear key", 0XA3 : "line input", 0XA4 : "input", 0XA5 : "clear", 0XA6 : "data", 0XA7 : "end", 0XA8 : "erase", 0XA9 : "reserve", 0XAA : "as datascreen", 0XAB : "as work", 0XAC : "as screen", 0XAD : "as data", 0XAE : "copy", 0XAF : "def", 0XB0 : "hide", 0XB1 : "show", 0XB2 : "change mouse", 0XB3 : "limit mouse", 0XB4 : "move x", 0XB5 : "move y", 0XB6 : "fix", 0XB7 : "bgrab", 0XB9 : "fill", 0XBA : "key list", 0XBB : "key speed", 0XBC : "move", 0XBD : "anim", 0XBE : "unfreeze", 0XBF : "set zone", 0XC0 : "reset zone", 0XC1 : "limit sprite", 0XC2 : "priority", 0XC3 : "reduce", 0XC4 : "put sprite", 0XC5 : "get sprite", 0XC6 : "load", 0XC7 : "save", 0XC8 : "palette", 0XC9 : "synchro", 0XCA : "error", 0XCB : "break", 0XCC : "let", 0XCD : "key", 0XCE : "open in", 0XCF : "open out", 0XD0 : "open", 0XD1 : "close", 0XD2 : "field", 0XD3 : "as", 0XD4 : "put key", 0XD5 : "get palette", 0XD6 : "kill", 0XD7 : "rename", 0XD8 : "rm dir", 0XD9 : "mk dir", 0XDA : "stop", 0XDB : "wait vbl", 0XDC : "sort", 0XDD : "get", 0XDE : "flash", 0XDF : "using", 0XE0 : "lprint", 0XE1 : "auto back", 0XE2 : "set line", 0XE3 : "gr writing", 0XE4 : "set mark", 0XE5 : "set paint", 0XE7 : "set pattern", 0XE8 : "clip", 0XE9 : "arc", 0XEA : "polygon", 0XEB : "circle", 0XEC : "earc", 0XED : "epie", 0XEE : "ellipse", 0XEF : "writing", 0XF0 : "paint", 0XF1 : "ink", 0XF2 : "wait", 0XF3 : "click", 0XF4 : "put", 0XF5 : "zoom", 0XF6 : "set curs", 0XF7 : "scroll down", 0XF8 : "scroll up", 0XF9 : "scroll", 0XFA : "inverse", 0XFB : "shade", 0XFC : "windopen", 0XFD : "window", 0XFE : "windmove", 0XFF : "windel"};
const EXTENDED_FUNCTIONS = {0X80 : "hsin", 0X81 : "hcos", 0X82 : "htan", 0X83 : "asin", 0X84 : "acos", 0X85 : "atan", 0X86 : "upper$", 0X87 : "lower$", 0X88 : "current", 0X89 : "match", 0X8A : "errn", 0X8B : "errl", 0X8C : "varptr", 0X8D : "input$", 0X8E : "flip$", 0X8F : "free", 0X90 : "str$", 0X91 : "hex$", 0X92 : "bin$", 0X93 : "string$", 0X94 : "space$", 0X95 : "instr", 0X96 : "max", 0X97 : "min", 0X98 : "lof", 0X99 : "eof", 0X9A : "dir first$", 0X9B : "dir next$", 0X9C : "btst", 0X9D : "collide", 0X9E : "accnb", 0X9F : "language", 0XA1 : "hunt", 0XA2 : "true", 0XA3 : "false", 0XA4 : "xcurs", 0XA5 : "ycurs", 0XA6 : "jup", 0XA7 : "jleft", 0XA8 : "jright", 0XA9 : "jdown", 0XAA : "fire", 0XAB : "joy", 0XAC : "movon", 0XAD : "icon$", 0XAE : "tab", 0XAF : "exp", 0XB0 : "charlen", 0XB1 : "mnbar", 0XB2 : "mnselect", 0XB3 : "windon", 0XB4 : "xtext", 0XB5 : "ytext", 0XB6 : "xgraphic", 0XB7 : "ygraphic", 0XB9 : "sqr", 0XBA : "divx", 0XBB : "divy", 0XBC : "ln", 0XBD : "tan", 0XBE : "drvmap", 0XBF : "file select$", 0XC0 : "dfree", 0XC1 : "sgn", 0XC2 : "port", 0XC3 : "pvoice", 0XC4 : "int", 0XC5 : "detect", 0XC6 : "deg", 0XC7 : "rad"};
/* eslint-enable max-len, unicorn/number-literal-case */

const lookup = (table, op) => (Object.hasOwn(table, op) ? table[op].toUpperCase() : `UNKNOWN OP: 0x${op.toString(16).toUpperCase()}`);

const br = new UInt8ArrayReader(await Deno.readFile(argv.inputFilePath));

const out = {};

// Source code info: https://temlib.org/AtariForumWiki/index.php/STOS.BAS
if(br.str(10)!=="Lionpoulos")
	Deno.exit(console.log(`Error: Magic string 'Lionpoulos' not found!`));

const srcLen = br.uint32();
console.log(`Tokenized code is ${srcLen} bytes long`);

br.skip(4);			// Ignore: Offset to first memory bank
br.skip(15*(1+3));	// Ignore: Bank types and lengths

while(!br.eof())
{
	const lineLen = br.uint16()-4;
	if(lineLen===-4)
		break;

	const lineNum = br.uint16();
	const linebr = br.sub(lineLen);
	
	const op = linebr.uint8();
	switch(op)
	{
		case 0x8A:
			linebr.skip(1);	// Unknown Purpose
			out[lineNum] = `REM ${linebr.str(lineLen-3)}`;	// Skip op, unknown and trailing 0x00
			break;
		case 0xFA:
			out[lineNum] = `VARNAME`;
			break;
		case 0xFB:
			out[lineNum] = `INTEGER (BINARY)`;
			break;
		case 0xFC:
			out[lineNum] = `STRING LITERAL`;
			break;
		case 0xFD:
			out[lineNum] = `INTEGER (HEXADECIMAL)`;
			break;
		case 0xFE:
			out[lineNum] = `INTEGER`;
			break;
		case 0xFF:
			out[lineNum] = `FLOATING POINT NUMBER`;
			break;
		case 0xA8:
			out[lineNum] = `EXTENSION (Index #${linebr.uint8()}) (Token 0x${linebr.uint8().toString(16)})`;
			break;
		case 0xA0:
			out[lineNum] = lookup(EXTENDED_INSTRUCTIONS, linebr.uint8());
			break;
		case 0xB8:
			out[lineNum] = lookup(EXTENDED_FUNCTIONS, linebr.uint8());
			break;
		default:
			out[lineNum] = lookup(MAIN, op);
			break;
	}

	//if(argv.verbose && Object.hasOwn(out, lineNum))
	//	XU.log`${lineNum.toString()} ${out[lineNum]}`;
}

await Deno.writeTextFile(argv.outputFilePath, `${Object.entries(out).sortMulti([([lineNum]) => lineNum]).map(([lineNum, lineVal]) => `${lineNum} ${lineVal}`).join("\n")}\n`);
