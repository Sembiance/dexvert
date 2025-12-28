<?php
/**
 * A P3T file header. This contains data extracted from the first 128 bytes of the P3T file
 * @package PS3Theme.net
 * @subpackage P3T Extractor
 * @access public
 * @author Hoshang Sadiq
 * @copyright 2011
 * @todo All fields are public, should be private
 * 
 * @changelog
 * @version 1.1.1
 * @date 06/05/2011
 * @new Now allows custom echo's
 * 
 * @changelog
 * @version 1.1
 * @date 05/05/2011
 * @new added functions to echo the details, this changes depending on the sapi or STDIN
 * @new this now handles the echos
 * 
 * @version 1.0
 * @date 23/01/2011
 */

namespace P3TExtractor;

class Header {
    /**
     * Contains the first 4 characters of the P3T/RAF file
     * For RAF this is also RAFO, for P3T this is always P3TF
     * @var string
     */
    public $magic = '';
    /**
     * Unknown
     * @var int
     */
    public $version = 0;

    public $tree_offset = 0;
    public $tree_size = 0;
    public $idtable_offset = 0;
    public $idtable_size = 0;
    public $stringtable_offset = 0;
    public $stringtable_size = 0;
    public $intarray_offset = 0;
    public $intarray_size = 0;
    public $floatarray_offset = 0;
    public $floatarray_size = 0;
    public $filetable_offset = 0;
    public $filetable_size = 0;
    private $cli = false;
    private $echo;

    /**
     * Constructor
     * @param bool $echo Whether or not to echo errors etc
     */
    public function __construct($echo) {
        $this->cli = php_sapi_name() === 'cli' || defined('STDIN');
        $this->echo = $echo;
    }

    /**
     * Custom text echo
     * @param string $text          The text to echo
     * @param string|bool $color    The colour of the text
     * @param bool $ln              Whether or not to add a new line at the end
     */
    public function custom($text, $color = false, $ln = false) {
        if(!$this->echo) {
            return;
        }
        if($this->cli || !$color) {
            echo $text;
        } else {
            echo '<span style="color:'.$color.'">'.$text.'</span>';
        }
        if($ln) {
            echo "\n";
        }
    }

    /**
     * Custom text echo with a new line feed at the end
     * @param  string $text  The text to echo
     * @param  string|bool $color The colour of the text
     */
    public function writeln($text, $color = false) {
        $this->custom($text, $color, true);
    }

    /**
     * Simply writes OK with a color
     * @see Header::writeln()
     */
    public function success() {
        $this->writeln('Ok', '#006600');
    }

    /**
     * Simply writes Failed with a color
     * @see Header::writeln()
     */
    public function failed() {
        $this->writeln('Failed', '#FF0000');
    }

    /**
     * Simply writes Ignored with a color
     * @see Header::writeln()
     */
    public function ignored() {
        $this->writeln('Ignored', '#FF8000');
    }

    /**
     * Writes a line with a file
     */
    public function write($file) {
        $file = ($this->cli) ? $file : '<strong>'.$file.'</strong>';
        $this->custom('Writing ' . $file . ': ');
    }
}

