import {xu, fg} from "xu";
import {fileUtil} from "xutil";
import {path, assertStrictEquals, delay} from "std";
import {Format} from "../../src/Format.js";
import {families} from "../../src/family/families.js";
import {XLog} from "xlog";
import {TEXT_MAGIC_STRONG} from "../../src/Detection.js";

const formats = {};
export {formats};

let initCalled = false;

export const formatDirPath = path.join(import.meta.dirname, "..", "..", "src", "format");

async function loadFormatFilePath(formatFilePath, {reload}={})
{
	if(formatFilePath.endsWith("formats.js"))
		return;

	const formatModule = await import(reload ? `${formatFilePath}#${Date.now() + performance.now()}` : formatFilePath);
	const formatid = Object.keys(formatModule).find(k => k.at(0)!=="_");
	const familyid = path.basename(path.dirname(formatFilePath));
	if(!families[familyid])
		throw new Error(`format [${formatid}] at [${formatFilePath}] is in a directory [${familyid}] that does not have a family class`);

	// class name must match filename
	assertStrictEquals(formatid, path.basename(formatFilePath, ".js"), `format file [${formatFilePath}] does not have a matching class name [${formatid}]`);

	// check for duplicates
	if(!reload && formats[formatid])
		throw new Error(`format [${formatid}] at [${formatFilePath}] is a duplicate`);

	// create the class and validate it
	const format = formatModule[formatid].create(families[familyid]);
	if(!(format instanceof Format))
		throw new Error(`format [${formatid}] at [${formatFilePath}] is not of type Format`);

	// some manual checks on meta providers based on what converters are being used
	for(const [converter, metaProvider] of Object.entries({"convert" : "image", "darktable_cli" : "darkTable"}))
	{
		const allowFormatsMetaMismatch = ["ttf", "otf", "pcd"];
		if(Array.isArray(format.converters) && format.converters.some(v => v===converter || (typeof v==="string" && v.startsWith(`${converter}[`))) && !(format.metaProvider || []).includes(metaProvider) && !allowFormatsMetaMismatch.includes(formatid))
			throw new Error(`format ${formatid} has ${converter} as a converter, but NOT ${metaProvider} as a metaProvider.`);
	}

	if(format.ext)
	{
		const invalidExtensions = format.ext.filter(ext => ext!==ext.toLowerCase());
		if(invalidExtensions.length>0)
			throw new Error(`format ${formatid} has invalid extensions (SHOULD always be LOWERCASE): ${invalidExtensions}`);
	}


	if(Object.hasOwn(format, "forbidExtMatch") && !Object.hasOwn(format, "ext"))
		throw new Error(`format ${formatid} has forbidExtMatch, but no ext`);

	formats[formatid] = format;
}

const unsupportedFormatids = new Set();
async function loadUnsupported({reload}={})
{
	if(reload)
	{
		for(const formatid of unsupportedFormatids)
			delete formats[formatid];
		unsupportedFormatids.clear();
	}

	const {default : unsupported} = await import(reload ? `./unsupported.js#${Date.now() + performance.now()}` :"./unsupported.js");
	for(const [familyid, unsupportedFormats] of Object.entries(unsupported))
	{
		for(const [formatid, o] of Object.entries(unsupportedFormats))
		{
			if(formats[formatid])
				throw new Error(`format [${formatid}] in unsupported.js is a duplicate of ${formats[formatid]}`);

			const supportedKeys = ["ext", "filename", "forbiddenMagic", "idMeta", "magic", "matchPreExt", "name", "notes", "weakFilename", "weakMagic", "website"];
			const extraKeys = Object.keys(o).subtractAll(supportedKeys);
			if(extraKeys.length>0)
				throw new Error(`unsupported format ${familyid}/${formatid} has extra keys that are not currently copied over to the Unknown class, add them: ${extraKeys}`);
			
			class Unsupported extends Format
			{
				unsupported = true;
			}

			formats[formatid] = Unsupported.create(families[familyid], format =>	// eslint-disable-line sembiance/shorter-arrow-funs
			{
				for(const supportedKey of supportedKeys)
				{
					if(Object.hasOwn(o, supportedKey))
						format[supportedKey] = o[supportedKey];
				}
			});
			formats[formatid].formatid = formatid;
			unsupportedFormatids.add(formatid);
		}
	}
}

const simpleFormatids = new Set();
async function loadSimple({reload}={})
{
	if(reload)
	{
		for(const formatid of simpleFormatids)
			delete formats[formatid];
		simpleFormatids.clear();
	}

	const {default : simple} = await import(reload ? `./simple.js#${Date.now() + performance.now()}` :"./simple.js");
	for(const [familyid, simpleFormats] of Object.entries(simple))
	{
		for(const [formatid, o] of Object.entries(simpleFormats))
		{
			if(formats[formatid])
				throw new Error(`format [${formatid}] in simple.js is a duplicate`);

			const supportedKeys = ["ext", "filename", "forbiddenMagic", "idMeta", "magic", "name", "trustMagic", "weakFilename", "weakMagic", "website"];
			const extraKeys = Object.keys(o).subtractAll(supportedKeys);
			if(extraKeys.length>0)
				throw new Error(`simple format ${familyid}/${formatid} has extra keys that are not currently copied over to the Simple class, add them: ${extraKeys}`);
			
			class Simple extends Format
			{
				converters = ["strings"];
				packed     = true;
				simple     = true;
			}

			formats[formatid] = Simple.create(families[familyid], format =>
			{
				for(const supportedKey of supportedKeys)
				{
					if(Object.hasOwn(o, supportedKey))
						format[supportedKey] = o[supportedKey];
				}
				if(o.ext?.length)
					format.forbidExtMatch = true;
			});
			formats[formatid].formatid = formatid;
			simpleFormatids.add(formatid);
		}
	}
}

const gameArchiveFormatids = new Set();
async function loadGameArchive({reload}={})
{
	if(reload)
	{
		for(const formatid of gameArchiveFormatids)
			delete formats[formatid];
		gameArchiveFormatids.clear();
	}

	const gameArchiveImport = await import(reload ? `./gameArchive.js#${Date.now() + performance.now()}` :"./gameArchive.js");

	for(const converterType of ["gameextractor", "gamearch", "both"])
	{
		const gameArchiveFamilyFormats = gameArchiveImport[converterType];
		for(const [familyid, gameArchiveFormats] of Object.entries(gameArchiveFamilyFormats))
		{
			for(const [formatid, o] of Object.entries(gameArchiveFormats))
			{
				if(formats[formatid])
					throw new Error(`format [${formatid}] in gameArchive.js is a duplicate`);

				const allowExtMatch = !!o.allowExtMatch;
				delete o.allowExtMatch;

				const supportedKeys = ["ext", "filename", "forbiddenMagic", "idMeta", "magic", "name", "trustMagic", "weakMagic", "website"];
				const extraKeys = Object.keys(o).subtractAll(supportedKeys);
				if(extraKeys.length>0)
					throw new Error(`gameArchive format ${familyid}/${formatid} has extra keys that are not currently copied over to the GameArchive class, add them: ${extraKeys}`);
				
				class GameArchive extends Format
				{
					converters = [];
				}

				formats[formatid] = GameArchive.create(families[familyid], format =>
				{
					for(const supportedKey of supportedKeys)
					{
						if(Object.hasOwn(o, supportedKey))
							format[supportedKey] = o[supportedKey];
					}
					if(o.ext?.length && !allowExtMatch)
						format.forbidExtMatch = true;

					if(["both", "gamearch"].includes(converterType))
						format.converters.push("gamearch");
					if(["both", "gameextractor"].includes(converterType))
						format.converters.push("gameextractor");
				});

				formats[formatid].formatid = formatid;
				gameArchiveFormatids.add(formatid);
			}
		}
	}
}

const packedFormatids = new Set();
async function loadPacked({reload}={})
{
	if(reload)
	{
		for(const formatid of packedFormatids)
			delete formats[formatid];
		packedFormatids.clear();
	}

	const packedImport = await import(reload ? `./packed.js#${Date.now() + performance.now()}` :"./packed.js");

	for(const converterType of ["unp", "cup386", "both"])
	{
		const packedFamilyFormats = packedImport[converterType];
		for(const [familyid, packedFormats] of Object.entries(packedFamilyFormats))
		{
			for(const [formatid, o] of Object.entries(packedFormats))
			{
				if(formats[formatid])
					throw new Error(`format [${formatid}] in packed.js is a duplicate`);

				const supportedKeys = ["filename", "forbiddenMagic", "magic", "name", "trustMagic", "weakMagic", "website"];
				const extraKeys = Object.keys(o).subtractAll(supportedKeys);
				if(extraKeys.length>0)
					throw new Error(`packed format ${familyid}/${formatid} has extra keys that are not currently copied over to the Packed class, add them: ${extraKeys}`);
				
				class Packed extends Format
				{
					converters     = [];
					ext            = [".exe", ".com"];
					packed         = true;
					forbidExtMatch = true;
				}

				formats[formatid] = Packed.create(families[familyid], format =>
				{
					for(const supportedKey of supportedKeys)
					{
						if(Object.hasOwn(o, supportedKey))
							format[supportedKey] = o[supportedKey];
					}

					if(["both", "unp"].includes(converterType))
						format.converters.push("unp[renameKeepFilename]");
					if(["both", "cup386"].includes(converterType))
						format.converters.push("cup386[renameKeepFilename]");
				});

				formats[formatid].formatid = formatid;
				packedFormatids.add(formatid);
			}
		}
	}
}

const textFormatids = new Set();
async function loadText({reload}={})
{
	if(reload)
	{
		for(const formatid of textFormatids)
			delete formats[formatid];
		textFormatids.clear();
	}

	const {default : text} = await import(reload ? `./text.js#${Date.now() + performance.now()}` :"./text.js");
	for(const [familyid, textFormats] of Object.entries(text))
	{
		for(const [formatid, o] of Object.entries(textFormats))
		{
			if(formats[formatid])
				throw new Error(`format [${formatid}] in text.js is a duplicate`);

			const supportedKeys = ["ext", "filename", "forbiddenMagic", "idMeta", "magic", "name", "trustMagic", "weakFilename", "weakMagic", "website"];
			const extraKeys = Object.keys(o).subtractAll(supportedKeys);
			if(extraKeys.length>0)
				throw new Error(`text format ${familyid}/${formatid} has extra keys that are not currently copied over to the Text class, add them: ${extraKeys}`);
			
			class Text extends Format
			{
				metaProvider = ["text"];
			}

			formats[formatid] = Text.create(families[familyid], format =>
			{
				for(const supportedKey of supportedKeys)
				{
					if(Object.hasOwn(o, supportedKey))
						format[supportedKey] = o[supportedKey];
				}
				if(o.ext?.length && o.magic?.length)
					format.forbidExtMatch = true;
				
				// for text based idMeta checks, we often end up matching binary rsrc files too, so if that's why we identified as this, ensure we are only untouched if we've also matched as TEXT (or another magic on it)
				if(o.idMeta)
				{
					format.untouched = dexState => dexState.id?.matchType!=="idMeta" || dexState.hasMagics(TEXT_MAGIC_STRONG) || (o.magic?.length && dexState.hasMagics(o.magic));
					format.priority = format.PRIORITY.LOWEST;
				}
				else
				{
					format.untouched = true;
					format.priority = format.PRIORITY.LOW;
				}
			});
			formats[formatid].formatid = formatid;
			textFormatids.add(formatid);
		}
	}
}

export async function init(xlog=new XLog("info"))
{
	if(initCalled)
		return;
	initCalled = true;

	const formatFilePaths = await fileUtil.tree(formatDirPath, {nodir : true, regex : /[^/]+\/.+\.js$/});
	xlog.info`Loading ${formatFilePaths.length} format files...`;
	await Promise.all(formatFilePaths.map(loadFormatFilePath).concat([loadUnsupported(), loadSimple(), loadGameArchive(), loadPacked(), loadText()]));
	xlog.debug`Loaded ${Object.keys(formats).length} formats`;
}

export async function formatChanged({type, filePath}, xlog=new XLog("info"))
{
	if(!filePath || filePath.endsWith("formats.js"))
		return;

	if(type==="create" || type==="modify")
	{
		try
		{
			if(path.basename(filePath)==="unsupported.js")
			{
				await loadUnsupported({reload : true});
			}
			else if(path.basename(filePath)==="simple.js")
			{
				await loadSimple({reload : true});
			}
			else if(path.basename(filePath)==="gameArchive.js")
			{
				await loadGameArchive({reload : true});
			}
			else if(path.basename(filePath)==="packed.js")
			{
				await loadPacked({reload : true});
			}
			else if(path.basename(filePath)==="text.js")
			{
				await loadText({reload : true});
			}
			else
			{
				await delay(250);	// give the file time to finish writing, most important for newly created files
				await loadFormatFilePath(filePath, {reload : type==="modify", create : type==="create"});
			}

			xlog.info`${fg.violet("RELOADED")} format/${path.relative(formatDirPath, filePath)}`;
		}
		catch(err) { xlog.error`FAILED to RELOAD format: ${filePath} error: ${err}`; }
	}
	else if(type==="delete")
	{
		delete formats[path.basename(filePath, ".js")];
		xlog.info`${fg.violet("UNLOADED")} format/${path.relative(formatDirPath, filePath)}`;
	}
}
