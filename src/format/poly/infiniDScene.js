import {Format} from "../../Format.js";

export class infiniDScene extends Format
{
	name        = "Infini-D Scene";
	website     = "http://fileformats.archiveteam.org/wiki/Infini-D";
	ext         = [".ids", ".id4"];
	magic       = ["Infini-D Scene File", "Infini-D scene"];
	unsupported = true;
	notes       = "Most of it's life was a Mac only app. Later a version was released for windows, but it crashes in my 86box vms due to 'not enough RAM' which is likely a bug because it has too much RAM available.";
}
