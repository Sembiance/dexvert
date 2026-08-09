/* eslint-disable require-await, camelcase */
import {xu} from "xu";
import {path, dateFormat} from "std";
import {fileUtil, webUtil, printUtil, runUtil} from "xutil";
import {programs, init as initPrograms} from "../../src/program/programs.js";
import {_SKIP_CODES} from "../../src/program/detect/gameextractorID.js";
import {C} from "../../src/C.js";

export default async function programsFormats(xlog)
{
	await initPrograms(xlog);

	let results = [`Generated on: ${dateFormat(new Date(), "yyyy-MM-dd")}`, ""];

	// linux programs
	results.push(printUtil.majorHeader("Linux"));
	// each function entry should be in the format:   dexvertProgram__portagePackage1__portagePackage2...   (don't need to specify a portagePackage unless different than dexvertProgram name)  Use DASH to represent a '-' in the portage name
	results = results.concat(await [
		async function aaru__Aaru() { return (await runUtil.run("aaru", ["formats"])).stdout.match(/(filters \([\s\S]+)/)[1]; },
		async function abydosconvert__abydos()
		{
			const formats = [];
			for(const row of Array.from(xu.fromHTML(await webUtil.scrape("http://snisurset.net/code/abydos/supported.html")).querySelectorAll(".widecontent table.grid tr")))
			{
				const [formatName, mimeType, extensions, supported] = (Array.from(row.querySelectorAll("td")) || []).map(c => c.textContent.trim());
				if(supported?.trim()?.length && supported.trim().toLowerCase()!=="no")
					formats.push({formatName, extensions, mimeType, supported});
			}
			return printUtil.columnizeObjects(formats);
		},
		async function adplay__adplay__adplug()
		{
			const adplayListDirPath = path.join(import.meta.dirname, "programsFormats", "adplayList");
			await runUtil.run("make", ["clean"], {cwd : adplayListDirPath});
			await runUtil.run("make", [], {cwd : adplayListDirPath});
			return (await runUtil.run("./adplayList", [], {cwd : adplayListDirPath})).stdout.trim().split("\n").sortMulti().join("\n");
		},
		async function amigadepacker() { return ["PowerPacker", "XPK", "SQSH", "MMCMP", "StoneCracker 4.04 (S404)"].join("\n"); },
		async function ancient()
		{
			const readmeData = (await runUtil.run("bzcat", [path.join((await fileUtil.tree("/usr/share/doc", {depth : 1, nofile : true, regex : /^ancient-/}))[0], "README.md.bz2")])).stdout;
			return readmeData.match(/Decompression algorithms provided:([\s\S]+)Special thanks go to/)[1];
		},
		async function ansilove__libansilove()
		{
			const readmeData = (await runUtil.run("bzcat", [path.join((await fileUtil.tree("/usr/share/doc", {depth : 1, nofile : true, regex : /^libansilove-/}))[0], "README.md.bz2")])).stdout;
			return readmeData.match(/The following formats are supported:([\s\S]+)# Documentation/)[1];
		},
		async function asapconv__asap()
		{
			const readmeData = (await runUtil.run("bzcat", [path.join((await fileUtil.tree("/usr/share/doc", {depth : 1, nofile : true, regex : /^asap-/}))[0], "README.bz2")])).stdout;
			return readmeData.match(/ASAP supports the following file formats:([\s\S]+)and is available on/)[1].strip("\n").replaceAll(/,\s?/g, "\n");
		},
		async function assimp() { return (await runUtil.run("assimp", ["listinfo"])).stdout; },
		async function convert__imagemagick()
		{
			const formats = [];
			for(const row of Array.from(xu.fromHTML(await fileUtil.readTextFile(path.join((await fileUtil.tree("/usr/share/doc", {depth : 1, nofile : true, regex : /^imagemagick-/}))[0], "html/www/formats.html"))).querySelectorAll("table tr")))
			{
				const [tag, mode, description, notes] = (Array.from(row.querySelectorAll("td")) || []).map(c => c.textContent.trim().replaceAll("\n", ""));
				if(tag?.trim()?.length)
					formats.push({tag, mode, description, notes});
			}
			return printUtil.columnizeObjects(formats);
		},
		async function darktable() { return (await runUtil.run("darktable-cli", ["--list-formats"])).stdout.match(/supported input formats:([\s\S]+)/)[1].split("\n").map(v => v.trim()).join("\n"); },
		async function deark() { return (await runUtil.run("bzcat", [path.join((await fileUtil.tree("/usr/share/doc", {depth : 1, nofile : true, regex : /^deark-/}))[0], "formats.txt.bz2")])).stdout; },
		async function dragonUnpacker() { return (await xu.fetch(`http://${C.DRAGON_UNPACKER_HOST}:${C.DRAGON_UNPACKER_PORT}/list`)).match(/(Extensions[\s\S]+)/)[1]; },
		async function dskconv__libdsk() { return (await runUtil.run("dskconv", ["-types"])).stdout.match(/Disk image types supported:([\s\S]+)/)[1].split("\n").map(v => v.trim()).join("\n"); },
		async function ebook_convert__calibreDASHbin() { return (await runUtil.run(path.join(import.meta.dirname, "programsFormats", "calibreListFormats.py"), [])).stdout.match(/(Format \/ provider[\s\S]+)/)[1]; },
		async function ffmpeg() { return `${(await runUtil.run("ffmpeg", ["-formats"])).stdout}\n${(await runUtil.run("ffmpeg", ["-codecs"])).stdout}`; },
		async function gamearch__libgamearchive() { return (await runUtil.run("gamearch", ["--list-types"])).stdout; },
		async function gameextractor()
		{
			const list = [];
			for(const {name, code, games, extensions} of await xu.fetch(`http://${C.GAMEEXTRACTOR_HOST}:${C.GAMEEXTRACTOR_PORT}/list`, {asJSON : true}))
			{
				if(_SKIP_CODES.has(code))
					continue;

				const o = {};
				o.code = code;
				o.name = "";
				if(code!==name)
					o.name = name;

				o.extensions = extensions.join(", ");
				o.games = games.join(", ");

				list.push(o);
			}

			return printUtil.columnizeObjects(list.sortMulti([o => o.code]), {alignment : { code : "r", name : "l", extensions : "l"}});
		},
		async function gameimg__libgamegraphics() { return (await runUtil.run("gameimg", ["--list-types"])).stdout; },
		//async function gamemap__libgamemaps() { return (await runUtil.run("gamemap", ["--list-types"])).stdout; },
		async function gamemus__libgamemusic() { return (await runUtil.run("gamemus", ["--list-types"])).stdout; },
		async function gametls__libgamegraphics() { return (await runUtil.run("gametls", ["--list-types"])).stdout; },
		async function GARbro__GARbroserver() { return await xu.fetch(`http://${C.GARBRO_HOST}:${C.GARBRO_PORT}/list`); },
		async function gimp() { return (await runUtil.run("python3", [path.join(import.meta.dirname, "programsFormats", "gimpListFormats.py")])).stdout.match(/(Format\s+[\s\S]+)/)[1]; },
		async function iio2png() { return (await runUtil.run("iio2png", ["--formats"])).stdout.match(/Supported formats:([\s\S]+)/)[1].split("\n").map(v => v.trim()).join("\n"); },
		async function iconvert__openimageio() { return (await runUtil.run("oiiotool", ["--list-formats"])).stdout.match(/All OIIO supported formats and their extensions:([\s\S]+)/)[1].split("\n").map(v => v.trim()).join("\n"); },
		async function kss2wav__libkss()
		{
			const formatsData = (await runUtil.run("bzcat", [path.join((await fileUtil.tree("/usr/share/doc", {depth : 1, nofile : true, regex : /^libkss-/}))[0], "README.md.bz2")])).stdout;
			return formatsData.match(/# Supported formats([\s\S]+)# How to build/)[1];
		},
		async function librempeg() { return `${(await runUtil.run("librempeg", ["-formats"])).stdout}\n${(await runUtil.run("librempeg", ["-codecs"])).stdout}`; },
		async function midistar2mp3__midistar2mid__midi_processing() { return ["GMF", "HMI", "HMP", "LDS", "MIDS", "MUS", "RIFF MIDI", "SYX", "XMI"].join("\n"); },
		async function na_eofdec() { return `${(await runUtil.run("na_eofdec", ["--list-input-formats"])).stdout}\n${(await runUtil.run("na_eofdec", ["--list-archive-formats"])).stdout}`; },
		async function na_game_tool() { return `${(await runUtil.run("na_game_tool", ["--list-input-formats"])).stdout}\n${(await runUtil.run("na_game_tool", ["--list-archive-formats"])).stdout}`; },
		async function nconvert() { return (await runUtil.run("nconvert", ["-help"])).stdout.match(/Available format:([\s\S]+)/)[1].split("\n").map(v => v.trim()).join("\n"); },
		async function nihav() { return (await runUtil.run("nihav-encoder", ["--list-decoders"])).stdout; },
		async function openmpt123() { return (await runUtil.run("openmpt123", ["--list-formats"])).stdout; },
		async function pabloDraw__pablodraw() { return (await runUtil.run("PabloDraw", ["--list-formats"])).stdout; },
		async function powerpaint() { return (await runUtil.run("java", ["-jar", "/mnt/compendium/DevLab/dexvert/bin/powerpaint.jar", "--list"])).stdout; },
		async function recoil2png__recoil() { return (await runUtil.run("recoil2png", ["--list"])).stdout; },
		async function scribus() { return (await runUtil.run("scribus-1.7", ["--list-formats"], {virtualX : true})).stdout.match(/(Document and vector format handlers[\s\S]+)Built-in export formats/)[1]; },
		async function sevenZip__p7zip() { return (await runUtil.run("7z", ["i"])).stdout.match(/Formats:([\s\S]+)/)[1]; },
		async function soffice__libreoffice() { return (await runUtil.run("python3", [path.join(import.meta.dirname, "programsFormats", "sofficeListFormats.py")])).stdout; },
		async function sox__sox_ng() { return (await runUtil.run("sox", ["--help-format", "all"])).stdout; },
		async function unar() { return (await runUtil.run("unar", ["--list-formats"])).stdout; },
		async function uniconvertor__uniconvertorDASHappimage() { return (await runUtil.run("uniconvertor", ["--help"])).stdout.match(/INPUT FILE FORMATS-+([\s\S]+)---OUTPUT FILE FORMATS/)[1]; },
		async function vgmstream__vgmstreamDASHcli()
		{
			const formatsData = (await runUtil.run("bzcat", [path.join((await fileUtil.tree("/usr/share/doc", {depth : 1, nofile : true, regex : /^vgmstream-cli-/}))[0], "FORMATS.md.bz2")])).stdout;
			return formatsData.match(/### List([\s\S]+)Sometimes standard codecs/)[1];
		},
		async function view64() { return (await runUtil.run("view64pnm", ["--help-formats"])).stdout.match(/supports the following formats:([\s\S]+)/)[1]; },
		async function wuimg() { return (await runUtil.run("wuconv", ["--fmts"])).stderr; },
		async function xmp__libxmp() { return (await runUtil.run("bzcat", [path.join((await fileUtil.tree("/usr/share/doc", {depth : 1, nofile : true, regex : /^libxmp-/}))[0], "formats.txt.bz2")])).stdout; },
		async function zxtune()
		{
			const formats = [];
			let format = {};
			for(const line of (await runUtil.run("zxtune123", ["--list-plugins"])).stdout.match(/Supported plugins:([\s\S]+)/)[1].split("\n"))
			{
				const {key, value} = line.match(/^(?<key>[^:]+):\s*(?<value>.*)$/)?.groups || {};
				if(!key?.length)
					continue;
				if(Object.hasOwn(format, key.toLowerCase()))
				{
					formats.push(format);
					format = {};
				}

				format[key.toLowerCase()] = value;
			}
			if(Object.keys(format).length)
				formats.push(format);
			return printUtil.columnizeObjects(formats.sortMulti([o => o.plugin]));
		}
	].parallelMap(async fun =>
	{
		const [programName, ...portageNames] = fun.name.split("__");
		if(portageNames.length===0)
			portageNames.push(programName);
		portageNames.mapInPlace(v => v.replaceAll("DASH", "-"));
		xlog.info`Building program: ${programName}`;
		let programData = (await fun())?.trim();
		if(!programData?.length)
			Deno.exit(xlog.error`No data returned for ${programName} - aborting`);
		programData = programData.replaceAll(/[‘’]/g, "'").replaceAll("–", "-");
		return `>>> ${programName} ::: ${(await portageNames.parallelMap(async portageName => (await runUtil.run("portageq", ["best_version", "/", portageName])).stdout.trim())).join("  ")}${programs[programName]?.website ? ` ::: ${programs[programName].website}` : ""}\n${programData}\n\n`;
	}));

	for(const platform of ["Linux", "DOS", "wine", "Windows", "AtariST", "MacOS-X"])
	{
		xlog.info`Building platform: ${platform}...`;
		results.push(printUtil.majorHeader(platform));
		results.push(await fileUtil.readTextFile(path.join(import.meta.dirname, "programsFormats", `${platform}.txt`)));
	}

	await fileUtil.writeTextFile(path.join(import.meta.dirname, "..", "..", "sandbox", "txt", "programsFormats.txt"), results.map(v => v.decolor()).join("\n"));

	await webUtil.scrapeStop();
}


/*


await fileUtil.searchReplace(path.join(import.meta.dirname, "..", "sandbox", "txt", "programs_formats.txt"), />>> gameextractor.*<<< gameextractor/s, `>>> gameextractor (run dra util/updateGameextractorFormats.js to update)\n${table}\n<<< gameextractor`);

*/
