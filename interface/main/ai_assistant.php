<?php

/**
 * AI Assistant - AgentForge Healthcare AI Agent
 *
 * Embeds the AgentForge AI healthcare assistant powered by LangChain + Gemini Pro.
 * Provides drug interaction checking, symptom lookup, provider search,
 * appointment availability, and insurance coverage tools.
 *
 * @package   OpenEMR
 * @link      https://www.open-emr.org
 * @author    Joe Panetta <joe@agentforge.dev>
 * @copyright Copyright (c) 2026 Joe Panetta
 * @license   https://github.com/openemr/openemr/blob/master/LICENSE GNU General Public License 3
 */

require_once("../globals.php");

use OpenEMR\Core\Header;

?>
<!DOCTYPE html>
<html>
<head>
    <title><?php echo xlt("AI Assistant"); ?></title>
    <?php Header::setupHeader(); ?>
    <style>
        body {
            margin: 0;
            padding: 0;
            overflow: hidden;
        }
        .ai-assistant-container {
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        .ai-assistant-header {
            background: #1a73e8;
            color: white;
            padding: 8px 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-shrink: 0;
        }
        .ai-assistant-header h4 {
            margin: 0;
            font-size: 16px;
        }
        .ai-assistant-header .badge {
            background: rgba(255,255,255,0.2);
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
        }
        .ai-assistant-disclaimer {
            background: #fff3cd;
            border-bottom: 1px solid #ffc107;
            padding: 6px 16px;
            font-size: 12px;
            color: #856404;
            flex-shrink: 0;
        }
        #agentforge-iframe {
            width: 100%;
            flex: 1;
            border: none;
        }
        .ai-error {
            display: none;
            padding: 40px;
            text-align: center;
            color: #666;
        }
        .ai-error h5 {
            color: #dc3545;
        }
    </style>
</head>
<body class="body_bottom">
    <div class="ai-assistant-container">
        <div class="ai-assistant-header">
            <h4><?php echo xlt("AgentForge AI Assistant"); ?></h4>
            <span class="badge"><?php echo xlt("Powered by LangChain + Gemini"); ?></span>
        </div>
        <div class="ai-assistant-disclaimer">
            <?php echo xlt("This AI assistant is for educational and informational purposes only. It does not provide medical diagnoses or replace professional medical advice. Always consult a qualified healthcare provider."); ?>
        </div>
        <iframe
            id="agentforge-iframe"
            src="//localhost:8501"
            title="<?php echo xla("AI Assistant"); ?>"
            onload="document.getElementById('ai-error').style.display='none';"
            onerror="document.getElementById('ai-error').style.display='block';">
        </iframe>
        <div id="ai-error" class="ai-error">
            <h5><?php echo xlt("AI Assistant Unavailable"); ?></h5>
            <p><?php echo xlt("The AgentForge AI service is not running. Please ensure the agentforge Docker service is started."); ?></p>
            <code>cd docker/development-easy && docker compose up agentforge</code>
        </div>
    </div>
</body>
</html>
