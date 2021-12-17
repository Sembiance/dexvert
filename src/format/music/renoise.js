import {Format} from "../../Format.js";

export class renoise extends Format
{
	name        = "Renoise Module";
	website     = "http://fileformats.archiveteam.org/wiki/Renoise_song";
	ext         = [".xrns", ".rns"];
	magic       = ["Renoise module"];
	notes       = "The XRNS format is just a ZIP file with samples inside as FLACS and a song XML. The archive/zip format will end up handling that. I tried using renoise program, but it doesn't have CLI conversion nor did it even work anyways to render a song. Sigh.";
	unsupported = true;
}
