<?php
/**
 * @author TheHosh
 * @copyright 2011
 *
 *
 * @changelog
 * @version 1.2
 * New faster(?) method of looping through the pixel data,
 *
 * @changelog
 * @version 1.1
 * @fixed the skewed icons issue where if the icon's width was not a multiple of 4, it would extract a skewed version.
 */


/**
 * Parses a .GIM file fro ma string and saves it as PNG.
 * -----
 * Technical information:
 * GIM are formatted as follows:
 *  - Starts with a 128 byte header
 *     - First 12 bytes contain file identifier
 *        - HEX: 2E 47 49 4D 31 2E 30 30 00 50 53 50
 *        - ASCII: .GIM1.00 PSP
 *           - Note this says PSP, but the GIM files in question
 *             are actually about GIM files for the PS3.
 *     - Width located at offset 72 and 73, height located at offset 74 and 75
 *        - 2 x 2 bytes/16 bit/short int
 *        - Big endian
 *        - Unsigned
 *        - PHP pack: n2
 *  - Offset 128 onwards contains raw RGBA data
 *    - Unsigned
 *    - PHP Pack: C4
 *    - 4 bytes/32 bit/int
 *       - Red/Green/Blue/Alpha
 *          - 1byte/8bit/char each
 *          - int 0 to 255
 *       - Note that alpha has some problems
 *          -   0 is completely transparant
 *          - 255 is completely opaque
 *          - PHP requires a 7 bit alpha for colouring where
 *             -   0 is completely opaque
 *             - 127 is completely transparant
 */

namespace P3TExtractor;

class Gim {
    /**
     * Holds all the data of the .gim file. This is a raw binary string.
     * The width is stored at offset 72 (big endian, 2 bytes/short int)
     * The height is stored at offset 74 (big endian, 2 bytes/short int)
     * @access private
     * @var string
     */
    private $data = '';

    /**
     * Holds all the header data of the .gim file. This is a raw binary string.
     * @access private
     * @var string
     */
    private $header = '';

    /**
     * Holds all the raw RGBA data of the .gim file. This is a raw binary string.
     * @access private
     * @var string
     */
    private $rgba = '';

    /**
     * Holds the width of the image after it has been parsed,
     * stored at offset 72 as short int big endian
     * @access private
     * @var int
     */
    private $width = 0;

    /**
     * Holds the height of the image after it has been parsed,
     * stored at offset 74 as short int big endian
     * @access private
     * @var int
     */
    private $height = 0;

    /**
     * Holds the width of the image after it has been parsed.
     * @param string $imagedata raw binary string containing the image data of
     * the .gim file
     * @throws Exception
     */
    public function __construct( $imagedata ) {
        $this->data = $imagedata; // save the data in field
        // check that this is indeed a .gim file.
        // First 4 bytes must read as .GIM to confirm this
        if ( substr( $this->data, 0, 4 ) != '.GIM' ) {
            throw new Exception( 'This data is not in GIM format' );
        }

        // Seperate the header from the RGBA data
        $this->header = substr( $this->data, 0, 128 );
        $this->rgba = substr( $this->data, 128 );

        // Get and save the dimensions.
        list( $this->width, $this->height ) = unpack( 'n2', substr( $this->header, 72, 76 ) );
    }

    /**
     * Save the image as a PNG file.
     * @param string $dest The destination of the file (including filename and extension)
     * @param string $type The type as to save the GIM image as. Can be png (default), gif or jpg          
     */
    public function save( $dest, $type = 'png' ) {
        // Create image of the same width and height as the gim file
        // This is unpacked in the constructor
        $img = imagecreatetruecolor( $this->width, $this->height );
        imagealphablending( $img, false ); // Disable alpha blending
        imagesavealpha( $img, true ); // We want to save this with an alpha channel

        // Create a transparant background
        $transparent = imagecolorallocatealpha( $img, 255, 255, 255, 127 );
        imagefill( $img, 0, 0, $transparent );

        // Fix for skewed images, It simply pads the image by making sure the width is read a multiple of 4
        if ( $this->width % 4 != 0 ) {
            $this->width = $this->width + ( 4 - ( $this->width % 4 ) );
        }

        // Fill by iterating through your raw RGBA pixel data
        for ( $y = 0; $y < $this->height; $y++ ) {
            for ( $x = 0; $x < $this->width; $x++ ) {
                $pos = ( ( $y * $this->width ) + $x) * 4;
                // extract RGBA data
                list( $red, $green, $blue, $alpha ) = unpack( 'C4', substr( $this->rgba, $pos, ( $pos+4 ) ) );

                // Alpha transprancy is saved as 8bit int where 0 is completely transparant
                // and 255 is completely opaque.
                // We fix this by subtracting 255 from alpha, remove minus sign (make it absolute)
                // then bitshift it to the right once to make it 7bit 
                $alpha = abs( $alpha - 255 ) >> 1;
                //((~((int)$alpha8)) & 0xff) >> 1

                // Define the colour
                $color = imagecolorallocatealpha( $img, $red, $green, $blue, $alpha );

                // Set the pixel with the colour
                imagesetpixel( $img, $x, $y, $color );
            }
        }

        // Save the image
        if ( $type === 'png' ) {
            imagepng( $img, $dest );
        } elseif ( $type === 'gif' ) {
            imagegif( $img, $dest );
        } elseif( $type === 'jpg' ) {
            imagejpeg( $img, $dest );
        }
        // Free up memory
        imagedestroy( $img );
    }
}

