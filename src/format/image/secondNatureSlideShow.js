import {Format} from "../../Format.js";

export class secondNatureSlideShow extends Format
{
	name        = "Second Nature Slide Show";
	ext         = [".cat"];
	magic       = ["Second Nature Slide Show"];
	unsupported = true;
	notes       = "Could probably spy on how the second nature DLL files are called when reading these files and figure out how to call the DLL myself with AutoIt. Meh.";
}
