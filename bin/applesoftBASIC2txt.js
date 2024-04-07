/* eslint-disable @stylistic/no-multi-spaces, no-bitwise */
import {xu} from "xu";
import {cmdUtil, fileUtil} from "xutil";
import {UInt8ArrayReader} from "UInt8ArrayReader";
import {XLog} from "xlog";

const xlog = new XLog("warn");

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Converts <input> as an Applesoft BASIC compiled file and converts to <output.bas>",
	args :
	[
		{argid : "inputFilePath", desc : "BASIC file to decompile", required : true},
		{argid : "outputFilePath", desc : "Path to output.bas", required : true}
	]});

// inspired by: https://github.com/AppleCommander/AppleCommander/blob/main/lib/ac-api/src/main/java/com/webcodepro/applecommander/util/ApplesoftTokenizer.java
const TOKENS =
[
	" END ",		" FOR ",	" NEXT ",	" DATA ",	" INPUT ",		" DEL ",
	" DIM ",		" READ ",	" GR ",		" TEXT ",	" PR# ",		" IN# ",
	" CALL ",		" PLOT ",	" HLIN ",	" VLIN ",	" HGR2 ",		" HGR ",
	" HCOLOR= ",	" HPLOT ",	" DRAW ",	" XDRAW ",	" HTAB ",		" HOME ",
	" ROT= ",		" SCALE= ",	" SHLOAD ",	" TRACE ",	" NOTRACE ",	" NORMAL ",
	" INVERSE ",	" FLASH ",	" COLOR= ",	" POP ",	" VTAB ",		" HIMEM: ",
	" LOMEM: ",		" ONERR ",	" RESUME ",	" RECALL ",	" STORE ",		" SPEED= ",
	" LET ",		" GOTO ",	" RUN ",	" IF ",		" RESTORE ",	" & ",
	" GOSUB ",		" RETURN ",	" REM ",	" STOP ",	" ON ",			" WAIT ",
	" LOAD ",		" SAVE ",	" DEF ",	" POKE ",	" PRINT ",		" CONT ",
	" LIST ",		" CLEAR ",	" GET ",	" NEW ",	" TAB( ",		" TO ",
	" FN ",			" SPC( ",	"  THEN ",	" AT ",		"  NOT ",		"  STEP ",
	" +",			" -",		" *",		"/",		" ^",			"  AND ",
	"  OR ",		" >",		" = ",		" <",		" SGN",			" INT",
	" ABS",			" USR",		" FRE",		" SCRN( ",	" PDL",			" POS",
	" SQR",			" RND",		" LOG",		" EXP",		" COS",			" SIN",
	" TAN",			" ATN",		" PEEK",	" LEN",		" STR$",		" VAL",
	" ASC",			" CHR$",	" LEFT$",	" RIGHT$",	" MID$ "
];

const reader = new UInt8ArrayReader(await Deno.readFile(argv.inputFilePath), {endianness : "le"});

let nextAddress = -1;
const output = [];
let done = false;
function nextToken()
{
	if(nextAddress===-1)
	{
		nextAddress = reader.uint16();
		xlog.info`nextAddress: ${nextAddress}  remaining: ${reader.remaining()}`;
		if(reader.remaining()<2)
		{
			done = true;
			return;
		}

		if(nextAddress===0)
			return;

		const lineNumber = reader.uint16();
		xlog.info`lineNumber: ${lineNumber}`;
		output.push(`${output.length>0 ? "\n" : ""}${lineNumber} `);
		return;
	}
	
	let token = reader.uint8();
	if(token===0)
	{
		xlog.info`token===0`;
		nextAddress = -1;
		return;
	}

	if((token & 0x80)!==0)
	{
		const idx = (token-0x80);
		xlog.info`token idx ${token} ${idx} ${TOKENS[idx]}`;
		output.push(TOKENS[idx] || `<UNKNOWN TOKEN>`);
		return;
	}
	
	if(":;,^+-*/".split("").includes(String.fromCharCode(token)))
	{
		xlog.info`operator ${String.fromCharCode(token)}`;
		output.push(String.fromCharCode(token));
		return;
	}

	let inString = false;
	while(true)
	{
		output.push(token<0x20 ? `<CTRL-0x${token.toString(16).padStart(2, "0")}>` : String.fromCharCode(token));
		if(token===0x22)
			inString = !inString;

		if(!reader.remaining())
			break;

		token = reader.uint8();
		if((token & 0x80)!==0 || token===0 || (!inString && [0x3A, 0x2C, 0x3B].includes(token)))
		{
			reader.rewind(1);
			break;
		}
	}
}

while(!done && reader.remaining())
	nextToken();

await fileUtil.writeTextFile(argv.outputFilePath, output.join(""));

//console.log(output.join(""));
