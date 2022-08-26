import {Format} from "../../Format.js";

export class pelicanPressArtwork extends Format
{
	name       = "Pelican Press Artwork Archive";
	website    = "https://www.amigafuture.de/app.php/asd/?asd_id=595%3f";
	magic      = ["Pelican Press artwork"];
	converters = ["iff_convert"];
}
