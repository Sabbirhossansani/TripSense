import React, { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const CITY_COORDINATES = {
  "Chittagong": [22.3485, 91.8385],
  "Cox's Bazar": [21.4272, 92.0058],
  "Sylhet": [24.8949, 91.8687],
  "Dhaka": [23.8103, 90.4125],
  "Paris": [48.8566, 2.3522],
  "Tokyo": [35.6762, 139.6503],
  "Bangkok": [13.7563, 100.5018],
  "Cairo": [30.0444, 31.2357],
  "Dubai": [25.2048, 55.2708],
  "Rome": [41.9028, 12.4964]
};

function createNumberedIcon(number, isSubstitute = false) {
  const bg = isSubstitute ? "#059669" : "#E85D2A";
  return L.divIcon({
    className: "custom-leaflet-marker",
    html: `
      <div style="
        position: relative;
        width: 34px;
        height: 34px;
        display: flex;
        align-items: center;
        justify-content: center;
      ">
        <div style="
          width: 32px;
          height: 32px;
          background: ${bg};
          border: 2.5px solid #ffffff;
          box-shadow: 0 4px 12px rgba(0,0,0,0.35);
          border-radius: 50% 50% 50% 4px;
          transform: rotate(-45deg);
          display: flex;
          align-items: center;
          justify-content: center;
        ">
          <span style="
            transform: rotate(45deg);
            color: #ffffff;
            font-size: 13px;
            font-weight: 800;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          ">${number}</span>
        </div>
      </div>
    `,
    iconSize: [34, 34],
    iconAnchor: [17, 34],
    popupAnchor: [0, -32]
  });
}

export default function LeafletMap({ spots = [], onSelectSpot, city = "Chittagong", isTabActive = true }) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersLayerRef = useRef(null);
  const polylineLayerRef = useRef(null);

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      const initialCenter = CITY_COORDINATES[city] || [22.3485, 91.8385];
      const map = L.map(mapContainerRef.current, {
        center: initialCenter,
        zoom: 12,
        zoomControl: false
      });

      // OpenStreetMap standard tiles (reliable, no API key watermark)
      L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
      }).addTo(map);

      // Add Zoom Control at top-right
      L.control.zoom({ position: "topright" }).addTo(map);

      markersLayerRef.current = L.layerGroup().addTo(map);
      polylineLayerRef.current = L.layerGroup().addTo(map);

      mapInstanceRef.current = map;
    } else {
      const center = CITY_COORDINATES[city] || [22.3485, 91.8385];
      mapInstanceRef.current.setView(center, 12);
    }

    // Attach ResizeObserver to auto-invalidate size on container expand or display change
    const resizeObserver = new ResizeObserver(() => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.invalidateSize();
      }
    });
    if (mapContainerRef.current) {
      resizeObserver.observe(mapContainerRef.current);
    }

    return () => {
      resizeObserver.disconnect();
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, [city]);

  // Invalidate map size when tab becomes active
  useEffect(() => {
    if (isTabActive && mapInstanceRef.current) {
      const timer = setTimeout(() => {
        mapInstanceRef.current?.invalidateSize();
      }, 120);
      return () => clearTimeout(timer);
    }
  }, [isTabActive]);

  // Update Markers & Route Polyline when spots change
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map || !markersLayerRef.current || !polylineLayerRef.current) return;

    markersLayerRef.current.clearLayers();
    polylineLayerRef.current.clearLayers();

    if (!spots || spots.length === 0) {
      const center = CITY_COORDINATES[city] || [22.3485, 91.8385];
      map.setView(center, 12);
      return;
    }

    const latLngs = [];

    spots.forEach((spot, index) => {
      if (typeof spot.latitude === "number" && typeof spot.longitude === "number") {
        const point = [spot.latitude, spot.longitude];
        latLngs.push(point);

        const isSub = Boolean(spot.is_weather_substitute);
        const icon = createNumberedIcon(index + 1, isSub);

        const marker = L.marker(point, { icon });

        // Popup content
        const popupContent = document.createElement("div");
        popupContent.style.minWidth = "170px";
        popupContent.style.fontFamily = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
        popupContent.innerHTML = `
          <div style="font-weight: 700; font-size: 13px; color: #1e293b; margin-bottom: 2px;">
            ${index + 1}. ${spot.name}
          </div>
          <div style="font-size: 11px; color: #59615E; margin-bottom: 6px;">
            ${spot.scheduled_slot || "Scheduled Stop"}
          </div>
          <div style="display: flex; gap: 4px; margin-bottom: 8px;">
            <span style="background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-size: 10px; color: #334155; font-weight: 600;">
              ${spot.category}
            </span>
            <span style="background: ${isSub ? '#ecfdf5' : '#FFF0EA'}; color: ${isSub ? '#047857' : '#CC4A1B'}; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 600;">
              ${isSub ? '🛡️ Indoor Swap' : (spot.estimated_cost_bdt === 0 ? 'Free' : `৳${spot.estimated_cost_bdt}`)}
            </span>
          </div>
          <button id="view-spot-${spot.id}" style="
            width: 100%;
            background: #E85D2A;
            color: #ffffff;
            border: none;
            padding: 5px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
          ">View Details & Why</button>
        `;

        marker.bindPopup(popupContent);
        marker.on("popupopen", () => {
          const btn = document.getElementById(`view-spot-${spot.id}`);
          if (btn && onSelectSpot) {
            btn.onclick = () => onSelectSpot(spot);
          }
        });

        marker.addTo(markersLayerRef.current);
      }
    });

    // Draw route polyline
    if (latLngs.length > 1) {
      const polyline = L.polyline(latLngs, {
        color: "#E85D2A",
        weight: 3.5,
        opacity: 0.85,
        dashArray: "6, 8"
      });
      polyline.addTo(polylineLayerRef.current);
    }

    // Fit map bounds
    if (latLngs.length > 0) {
      const bounds = L.latLngBounds(latLngs);
      map.fitBounds(bounds, {
        padding: [45, 45],
        maxZoom: 14
      });
    }

    // Invalidate map size after DOM render
    setTimeout(() => {
      map.invalidateSize();
    }, 150);
  }, [spots, onSelectSpot, city]);

  return (
    <div style={{ position: "relative", width: "100%", height: "100%", minHeight: "320px", borderRadius: "16px", overflow: "hidden" }}>
      <div ref={mapContainerRef} style={{ width: "100%", height: "100%", minHeight: "320px", zIndex: 1 }} />
      <div style={{
        position: "absolute",
        bottom: "12px",
        left: "12px",
        zIndex: 10,
        background: "rgba(255, 255, 255, 0.92)",
        backdropFilter: "blur(6px)",
        padding: "6px 12px",
        borderRadius: "20px",
        boxShadow: "0 2px 8px rgba(0,0,0,0.12)",
        display: "flex",
        alignItems: "center",
        gap: "10px",
        fontSize: "11px",
        fontWeight: 600,
        color: "#475569"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
          <span style={{ width: "10px", height: "10px", borderRadius: "50%", background: "#E85D2A", display: "inline-block" }}></span>
          <span>Day Route ({spots.length} Stops)</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
          <span style={{ width: "10px", height: "10px", borderRadius: "50%", background: "#059669", display: "inline-block" }}></span>
          <span>Weather Safe</span>
        </div>
      </div>
    </div>
  );
}
