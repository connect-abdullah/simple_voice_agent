#!/usr/bin/env python3
"""
Tests for the Voice Agent web frontend
"""
import pytest
import requests
import os
import time

class TestWebFrontend:
    """Test the web frontend server"""
    
    def test_frontend_server_running(self):
        """Test if frontend server is accessible"""
        try:
            response = requests.get("http://localhost:3000/", timeout=5)
            assert response.status_code == 200
            assert "Voice Agent" in response.text
            assert "🎤" in response.text
        except requests.exceptions.ConnectionError:
            pytest.skip("Frontend server not running on localhost:3000")
    
    def test_frontend_html_structure(self):
        """Test frontend HTML contains required elements"""
        try:
            response = requests.get("http://localhost:3000/", timeout=5)
            html = response.text
            
            # Check for essential elements
            assert 'id="voiceSelect"' in html
            assert 'id="recordBtn"' in html
            assert 'id="status"' in html
            assert "WebSocket" in html
            assert "ws://localhost:8000/stream" in html
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Frontend server not running on localhost:3000")

class TestIntegration:
    """Integration tests for the complete system"""
    
    def test_backend_frontend_connectivity(self):
        """Test that frontend can connect to backend"""
        try:
            # Test backend is running
            backend_response = requests.get("http://localhost:8000/", timeout=5)
            assert backend_response.status_code == 200
            
            # Test frontend is running
            frontend_response = requests.get("http://localhost:3000/", timeout=5)
            assert frontend_response.status_code == 200
            
            # Test frontend references correct backend URL
            assert "localhost:8000" in frontend_response.text
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Backend or frontend server not running")

if __name__ == "__main__":
    pytest.main([__file__])
