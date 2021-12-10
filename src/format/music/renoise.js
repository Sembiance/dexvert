import {Format} from "../../Format.js";

export class renoise extends Format
{
	name        = "Renoise Module";
	website     = "http://fileformats.archiveteam.org/wiki/Renoise_song";
	ext         = [".xrns", ".rns"];
	magic       = ["Renoise module"];
	notes       = "The XRNS format is just a ZIP file with samples inside as FLACS and a song XML. The archive/zip format will end up handling that. Ideally though I should buy Renoise and use that to generate an MP3.";
	unsupported = true;
}
