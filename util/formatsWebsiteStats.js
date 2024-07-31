import {xu} from "xu";
import {MediaWiki} from "MediaWiki";
import {XLog} from "xlog";
import {printUtil} from "xutil";
import {formats, init as initFormats} from "../src/format/formats.js";

const xlog = new XLog();

await initFormats(xlog);

const formatsWebsiteStats =
{
	"Unsupported"                        : [],
	"No Website"                         : [],
	"Other Website (Allowed)"            : [],
	"Other Website (Not Allowed)"        : [],
	"http://fileformats.archiveteam.org" : [],
	"https://wiki.multimedia.cx"         : [],
	"https://moddingwiki.shikadi.net"    : [],
	"https://en.wikipedia.org"           : [],
	"https://vgmpf.com"                  : []
};

const ALLOWED_OTHER_WEBSITE =
[
	"archive/appleDiskCopy",
	"archive/cso",
	"archive/dragonVDK",
	"archive/imageUSB",
	"archive/mgtFilesystem",
	"archive/pack200",
	"archive/pelicanPressArtwork",
	"archive/scummDigitizedSounds",
	"document/pcBoardPPE",
	"document/quill",
	"image/monsterBashTile",
	"music/amosTracker",
	"music/musiclineModule",
	"text/amigaDOSScript",
	"text/rexx",
	"text/uaem",
	"video/quake2Cinematic"
];

const COMMON_EXTENSIONS = [".cat", ".dbf", ".doc", ".ins", ".lib", ".msg", ".pat", ".txt"];

for(const [formatid, format] of Object.entries(formats))
{
	const familyFormat = `${formats[formatid].familyid}/${formatid}`;

	if(format.unsupported)
	{
		formatsWebsiteStats.Unsupported.push(familyFormat);
		continue;
	}

	if(!format.website)
	{
		formatsWebsiteStats["No Website"].push(familyFormat);
		continue;
	}

	let foundPrefix = false;
	for(const [websitePrefix, websiteFormats] of Object.entries(formatsWebsiteStats))
	{
		if(!websitePrefix.startsWith("http"))
			continue;

		if(format.website.startsWith(websitePrefix))
		{
			websiteFormats.push(familyFormat);
			foundPrefix = true;
			break;
		}
	}

	if(!foundPrefix)
	{
		if(ALLOWED_OTHER_WEBSITE.includes(familyFormat))
			formatsWebsiteStats["Other Website (Allowed)"].push(familyFormat);
		else
			formatsWebsiteStats["Other Website (Not Allowed)"].push(familyFormat);
	}
}

xlog.info`\nChecked ${Object.values(formatsWebsiteStats).flat().length.toLocaleString()} formats:`;
console.log(printUtil.columnizeObjects(Object.entries(formatsWebsiteStats).map(([k, v]) => ({type : k, count : v.length}))));

const ALLOWED_NO_SEMBIANCE_LINKS =
[
	// These pages are 'group' pages that link to sub-versions of the format
	"image/drHalo"
];

const wiki = new MediaWiki("http://fileformats.archiveteam.org/", {xlog});

async function checkFileFormatsArchiveTeamWiki()
{
	const results = [];
	
	xlog.info`Checking ${formatsWebsiteStats["http://fileformats.archiveteam.org"].length.toLocaleString()} 'File Formats ArchiveTeam' pages...`;
	const bar = printUtil.progress({barWidth : 35, max : formatsWebsiteStats["http://fileformats.archiveteam.org"].length});
	for(const familyFormat of formatsWebsiteStats["http://fileformats.archiveteam.org"])
	{
		const websiteURL = formats[familyFormat.split("/")[1]].website;

		const wikiPageTitle = websiteURL.substring("http://fileformats.archiveteam.org/wiki/".length);
		const content = await xu.tryFallbackAsync(async () => await wiki.getPage(wikiPageTitle));
		if(!content)
		{
			bar.tick();
			results.push(({familyFormat, websiteURL, why : "Failed to get page content"}));
			continue;
		}

		if(content.startsWith("#REDIRECT"))
		{
			bar.tick();
			results.push(({familyFormat, websiteURL, why : `Page is a redirect to: ${content.match(/^#REDIRECT \[\[(?<title>[^\]]+)]]$/)?.groups?.title?.replaceAll(" ", "_")}`}));
			continue;
		}

		if(!content.includes("{{DexvertSamples"))
		{
			bar.tick();
			if(!ALLOWED_NO_SEMBIANCE_LINKS.includes(familyFormat))
				results.push(({familyFormat, websiteURL, why : "No telparia links found"}));
			continue;
		}

		bar.tick();
	}

	if(results.length>0)
	{
		console.log("\n");
		console.log(printUtil.columnizeObjects(results.sortMulti([o => o.why]), {colNames : ["familyFormat", "websiteURL", "why"]}));
	}
}

async function lookForWebsite()
{
	const results = [];
	xlog.info`Searching for possible wiki pages for ${formatsWebsiteStats["No Website"].length.toLocaleString()} 'No Website' formats...`;
	const bar = printUtil.progress({barWidth : 35, max : formatsWebsiteStats["No Website"].length});
	for(const familyFormat of formatsWebsiteStats["No Website"])
	{
		const format = formats[familyFormat.split("/")[1]];
		let possibleTitles = await wiki.searchTitles(format.name);
		if(!possibleTitles?.length && format.ext?.some(v => !COMMON_EXTENSIONS.includes(v.toLowerCase())))
			 possibleTitles = await wiki.searchTitles(format.ext.find(v => !COMMON_EXTENSIONS.includes(v.toLowerCase())));

		if(possibleTitles?.length)
			results.push({familyFormat, possibleTitles : possibleTitles.length>3 ? `${possibleTitles.length} possibilities` : `[${possibleTitles.map(v => `http://fileformats.archiveteam.org/wiki/${encodeURIComponent(v)}`).join("] [")}]`});
		bar.tick();
	}

	if(results.length>0)
	{
		console.log("\n");
		console.log(printUtil.columnizeObjects(results.sortMulti([o => o.possibleTitles.startsWith("["), o => o.familyFormat], [true, false])));
	}
}

// Best to only run 1 check at a time, you choose, uncomment the one you want to run, then swap and run the other
//await checkFileFormatsArchiveTeamWiki();
//await lookForWebsite();
