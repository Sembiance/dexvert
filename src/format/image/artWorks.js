import {Format} from "../../Format.js";

export class artWorks extends Format
{
	name        = "ArtWorks Drawing";
	website     = "http://fileformats.archiveteam.org/wiki/Artworks";
	magic       = ["ArtWorks drawing"];
	notes       = "Viewer/Renderer: http://mw-software.com/software/awmodules/awrender.html";
	unsupported = true;
}
