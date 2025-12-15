<?php
/**
 * Plugin Name: Industrial AI Recommendation Engine
 * Description: AI-powered product recommendation chatbot for WooCommerce.
 * Version: 1.0.0
 * Author: Antigravity
 */

if (!defined('ABSPATH')) {
    exit; // Exit if accessed directly
}

class Industrial_AI_Recommendation {

    public function __construct() {
        // Enqueue scripts and styles
        add_action('wp_enqueue_scripts', array($this, 'enqueue_assets'));
        
        // Add widget to footer
        add_action('wp_footer', array($this, 'render_widget_container'));
    }

    public function enqueue_assets() {
        // Only load on frontend
        if (is_admin()) return;

        wp_enqueue_script(
            'industrial-ai-widget',
            plugin_dir_url(__FILE__) . 'assets/widget.js',
            array('jquery'), // Dependencies
            '1.0.0',
            true // In footer
        );

        wp_enqueue_style(
            'industrial-ai-styles',
            plugin_dir_url(__FILE__) . 'assets/widget.css',
            array(),
            '1.0.0'
        );

        // Pass PHP data to JS
        wp_localize_script('industrial-ai-widget', 'industrialAI', array(
            'apiUrl' => 'http://localhost:8000/api/v1', // Update with actual API URL in prod
            'nonce'  => wp_create_nonce('wp_rest')
        ));
    }

    public function render_widget_container() {
        ?>
        <div id="industrial-ai-chat-widget"></div>
        <?php
    }
}

new Industrial_AI_Recommendation();
