import {Format} from "../../Format.js";

export class axialisProScreensaverProducerProject extends Format
{
	name           = "Axialis Professional Screensaver Producer project";
	ext            = [".ssp"];
	forbidExtMatch = true;
	magic          = ["Axialis Professional Screensaver Producer project", "Axialis Screensaver :ssp:"];
	converters     = ["nconvert[format:ssp]"];
}
