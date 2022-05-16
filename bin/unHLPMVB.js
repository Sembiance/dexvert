import {xu} from "xu";
import {cmdUtil, fileUtil, runUtil} from "xutil";
import {path} from "std";
import {XLog} from "xlog";

const FLDINST_IMPORT_REGEX = /{\\field\s+{\\\*\\fldinst\s+import\s+(?<fileName>[^}]+)}}/g;
const BROKEN_IMAGE_PNG_HEX = "89504e470d0a1a0a0000000d4948445200000080000000800806000000c33e61cb00000006624b474400ff00ff00ffa0bda793000007e649444154789ced9d598c144518c77f3b3b1ec82e84851561e530410d284a44c1234262f08e4134f8200f5e892f02be299118828a068d313e29a031117d219c895114352a2831ec0262808807b80872392a2cee728e0fdf4c326c6666b7aabbaa7bbabf5f520f3b3bd5f5afeeff5477d7f11554a70e9800bc0c6c0076039d40de302deaa19c722cb22827aec957fd3b916bb41e5800dc805c432ba6005b2c44a801e255ffedc0f44a8564ca7cd608ac06d601e32c842bf1620cb00c58093474ff6777030c07be03a6bad7a578661a726d87957e586a8006e023e06a8fa214bf8c05d602fd8a1f941ae083c2179464330678aff847d100f7a0cd7e9a7800b813c40075c02b91ca51a26021509741def3af89588ce29f6b81f119b4e94f335333c0a4a85528913139035c1ab50a25325ab2c0e0100e741ad80be42afcbfdde298ed409bb5a2781176fd9b900e9dacb522612804eb673e00cc2c0852fcd204cc020e12ec1a5a676c0386b8aea5d2234381cd7836c001f4e2c789a1c0213c1a60a6976a2926ccc693014ea1f7fc3832107918776e805f3d554831673786d7b3dc84909ef82714a98a0b2abd8657c4c600798b3c8a1f8caf8d8d019404a10648396a8094a30648395960b1611e9b810dc50fab48ce009aa2288aa2288aa22889a10198036c023ab01bc3ce015f028f02f55ed59f4b3df058414b0ebbba7420e7e259a0af5ff9fe1907fc8edd89aa94be259c89ada65c026cb4d05b2ded41166c249211d84f5bea29b50217faab0a7d08360faf5a3a882cd34f1c2b7073c28a698ebfaaf09cc37ae491800e8962307006b7276d0f01e2e11850877487bbaccb19e416e31c5f8341377a286b0485850e8e69a15b940d071417ed3a278b7900a37624029509cd86dfb7e562609fe3327cd5c5a69cb9183e3f6481270d0b69c3dc00be5a1a1fe5f8aa8bcdebed3460bc49069d0f9072d40029470d9072d40029470d9072d40029470d9072d40029470d9072d40029470d90727c19a0cb53399d1eca48525dbc19608f87328ab10a5db31719af77cd6e0f657833c046e02fc7657c0d1c735c06c051e01bc7651c01be775c06e0cf00a7701b923e0fbce0f0f8dd79b150a62b1620e7cc0ba6d3955a2dcbc920ab575d4ca17ade525310e605d05b2dadc0fe87d96a519e3703804c405980ddde83e5d261646d40543c5ed010465d3a919625c83a076303d461de94b501d70710093249f43e64ff1a9bc51039644fc38f91851551d200dc8bac79b0899fd801ec4036ec3a18504b2b863382c06f0ba0b8c5b805d08ea094a30648396a8094a30648396a8094a30648396a8094a306483941b71dab15fa2191374623fb248e40165f9e07f4477e087f23c3bc87813f0ae927a4c7d1f548666424d500038029c01dc0646014c16207ec05d6039f019f229b662586a474055f808c2f2c034ee266a4aef41c3c8decd31327623f1ae882fe4884ad23b8bde8e55217125f212e317d526580bec04bd8879a0b339d04de060639ad71cfa4c6000f21f7e5a82f7cf79443b6738deaed2af1066804deafa02b4ee90bfcc42bea4ea20d3006f8b9971ae3900e216f203e49ec7c809b9059bfa3a216624033f2daf870d442aa510bfd007702ab093f126827f027f02f7016e93b68466e3361713eb01479605d12e2714325ceb78009c85cff309ae49dc042a4afa0dafd7910d281341f99ff783684b24f2311bc5c93a8678091049f717b0278078b8992255c09bc41f0d7cd4e6062001dbd213106c82251c0839cf065c065216a1a0cbc45b090b7bf211d57ae488c01e65be82aa61c6e9bdb5b09d607f1a1436d8930c028a4e9b639b9bb80cb1deb03690d82ec15709b235d8930806d58f99dc010c7da4a690436586add829bdec29a37c0440b3d79e46131ccfb7d6f69c2be73ca45ff40cd1b60a9859eb3485f41548cc5ee96b5d181969a36403332bc6aaae75d477a4c98875d2b705dc83a6ada00b32cb4fc87a79d357aa00fb01f73fd6f86aca3a6c702eeb6c8b384784ccfea045eb5c86753e7d089430bd007386ea165ac032db63461770b0b7380cbb805c8028b0d0b690f4b6d0913808b0cf36c057e74a0c5961cf00970bf61bec9c02f216958858c5fd41c4f61fecb792d12a5d5b1a9c7eb91282d10976780d11679d687ae223836d1c3ae0a5d85017131c01516797686ae2238bb308f216853f7d0888b014c63eb9cc6532045434e601eac72800b21bd252e06e867f8fd638809e248cef0fb8df8d9f1b42c713180e934ace34e54848369d4b27accdf801445511445511445512ca943d6b79bd08ef9f6f18a1fe66211ab200ec3c14a38d4f484102502d40029470d9072d40029c7c600918d5c293d627c6d6c0c10e9f8b55215abb885a6af81a7b0db1c4971cb20648e84f3d7c02c302304c14ab8ccc072cb39d316208f6c6f16451834a53c2dd84753b1ca940736a32688032dc87273dbeb689d318fc4c29b4dfc8226a7818148c0ea407194ea90756d4143b09d4166c3568aabbf0af301a4b9f889ace583b0eb3f101846b06d6601bab2c8e2ca91010f545f3846a5e3d82c571a4eb0e85e7122aef5df9701f6392e44892ffb33480856259d7c9501d644ad42898c35196013f043d44a14ef6c05366790d78139118b51fcf30c255dc16b8195118a51fcb21c5807e78e063e026c8b448ee2931dc013c53f4a0dd08184528f53d815255cb6017701478b1f741f0d6c076e466f07496439700bdde217941b0eee001e046e47061994da663bd2b24fa7ccd2f56a5bc67c8e74458e47225f4d42f6dd1d42f8dbb728e1d08504acdc8774f0ad41baa1f39532fc0f6274fa6b39c01d0d0000000049454e44ae426082";	// eslint-disable-line max-len
const xlog = new XLog();

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Processes <inputFilePath> as a Windows help or multimedia view book and processes it with helpdeco outputting an RTF and other embedded baggage files into <outputDirPath>",
	opts :
	{
		outFilename  : {desc : "Use this filename as the base for the output RTF", hasValue : true, defaultValue : "out"},
		extractExtra : {desc : "Set this to true to automatically extract any extra embedded files that are not referenced from the RTF file."}
	},
	args :
	[
		{argid : "inputFilePath", desc : "Windows HLP/MVB file", required : true},
		{argid : "outputDirPath", desc : "Output directory to place generated RTF and other non-referenced files into", required : true}
	]});

const inputFilePath = path.resolve(argv.inputFilePath);
const tmpDirPath = await fileUtil.genTempPath();

await Deno.mkdir(tmpDirPath);

// helpdeco doesn't extract all files though, we may need to extract ones that it didn't, first let's get a full accounting of the files available
const availableFilenames = new Set();

// some filenames are standard files which should be ignored, from: https://www.oocities.org/mwinterhoff/helpfile.htm
const NON_FILENAMES =
[
	"context", "ctxomap", "font", "kwbtree", "kwdata", "kwmap", "phrases", "system", "topic", "ttlbtree", "phrindex", "phrimage", "mvindex", "viola", "tomap", "rose", "topicid", "petra", "viola", "winpos", "pete", "flags", "cntjump", "cnttext",
	...[].pushSequence(0, 255).map(v => `cf${v}`)
];
const NON_FILENAME_SUFFIXES = ["wbtree", "wdata", "wmap", "kwbtree", "kwdata", "kwmap", ".gid", ".grp", ".tbl"];

const {stdout : fileListRaw} = await runUtil.run("helpdeco", ["-d", inputFilePath], {timeout : xu.MINUTE});
for(const fileListLine of fileListRaw.split("\n"))
{
	const {filename1, filename2} = fileListLine.trim().match(/^\|(?<filename1>\S+)\s+[^|]+\|\s\|(?<filename2>\S+)\s+/)?.groups || {};
	for(const filename of [filename1, filename2])
	{
		if(filename && !NON_FILENAMES.includes(filename.toLowerCase()) && !NON_FILENAME_SUFFIXES.some(suffix => filename.toLowerCase().endsWith(suffix)))
			availableFilenames.add(filename);
	}
}

// now let's try creating an RTF, doesn't always work, sometimes segfaults (RETIREA.HLP)
await runUtil.run("helpdeco", ["-r", "-y", inputFilePath], {cwd : tmpDirPath, timeout : xu.MINUTE*4});

const rtfFilePath = (await fileUtil.tree(tmpDirPath, {nodir : true, regex : /\.rtf$/i}))?.[0];	// we assume only 1 RTF file output, hopefully no MVB's embed actual RTF files in baggage
if(rtfFilePath && (await Deno.stat(rtfFilePath))?.size)
{
	// now load the the output RTF and go through and replace any image import commands with embedded hex data of the image so it's a self-contained RTF
	const rtfLines = (await fileUtil.readTextFile(rtfFilePath)).split("\n");

	const outputRTFFilePath = path.join(argv.outputDirPath, `${argv.outFilename}.rtf`);
	await Deno.writeTextFile(outputRTFFilePath, (await rtfLines.parallelMap(async rtfLine =>
	{
		rtfLine = await rtfLine.replaceAsync(FLDINST_IMPORT_REGEX, async (m, filename) =>	// eslint-disable-line no-param-reassign
		{
			const baseFilename = path.basename(filename, path.extname(filename));
			const importFilePath = path.join(tmpDirPath, filename);
			if(!(await fileUtil.exists(importFilePath)))
			{
				// helpdeco only auto extracts files it understands. so here we check to see if we have it available to extract manually and do so if needed
				if(!availableFilenames.has(baseFilename))
				{
					xlog.error`Import file missing: ${filename} at ${importFilePath}`;
					return `{\\pict\\pngblip\n${BROKEN_IMAGE_PNG_HEX}}`;
				}

				await runUtil.run("helpdeco", [inputFilePath, baseFilename, importFilePath]);
			}

			const convertDirPath = await fileUtil.genTempPath(tmpDirPath);
			await Deno.mkdir(convertDirPath);
			const {stdout, stderr} = await runUtil.run("dexvert", ["--json", importFilePath, convertDirPath], {timeout : xu.MINUTE*5, timeoutSignal : "SIGKILL", killChildren : true});
			const r = xu.parseJSON(stdout);
			if(!r?.created?.files?.output?.length)
			{
				xlog.error`Failed to convert import file ${filename} at ${importFilePath} with dexvert stdout ${stdout} and stderr ${stderr}`;
				return `{\\pict\\pngblip\n${BROKEN_IMAGE_PNG_HEX}}`;
			}

			if(r.created.files.output.length>1)
				xlog.warn`Only expected 1 result from import file ${filename} at ${importFilePath} conversion, but got several: ${r.created.files.output}`;

			const importOutputFile = r.created.files.output[0];
			if(importOutputFile.ext.toLowerCase()===".svg")
			{
				const svgWidth = r?.phase?.meta?.width || r?.phase?.meta?.canvasWidth || 100;
				const svgHeight = r?.phase?.meta?.height || r?.phase?.meta?.canvasHeight || 100;
				const tmpPNGFilePath = await fileUtil.genTempPath(tmpDirPath, ".png");
				await runUtil.run("resvg", ["--width", svgWidth.toString(), "--height", svgHeight.toString(), importOutputFile.absolute, tmpPNGFilePath]);
				availableFilenames.delete(baseFilename);
				return `{\\pict\\pngblip\n${(await Deno.readFile(tmpPNGFilePath)).asHex()}}`;
			}
			else if(importOutputFile.ext.toLowerCase()===".png")
			{
				availableFilenames.delete(baseFilename);
				return `{\\pict\\pngblip\n${(await Deno.readFile(importOutputFile.absolute)).asHex()}}`;
			}

			xlog.warn`Unexpected import conversion result from import file ${filename} at ${importFilePath} conversion. Got: ${importOutputFile}`;
			return `{\\pict\\pngblip\n${BROKEN_IMAGE_PNG_HEX}}`;
		});

		return rtfLine;
	})).join("\n"));
}

if(argv.extractExtra)
	await Array.from(availableFilenames).parallelMap(async availableFilename => await runUtil.run("helpdeco", [inputFilePath, availableFilename, path.join(argv.outputDirPath, availableFilename)]));

await fileUtil.unlink(tmpDirPath, {recursive : true});
