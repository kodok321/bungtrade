import { useState, useEffect, useRef, useCallback } from 'react'

export function useWebSocket(url) {
  const [data, setData] = useState(null)
  const [isConnected, setIsConnected] = useState(false)
  const wsRef = useRef(null)
  const activeRef = useRef(true)
  const reconnectTimeoutRef = useRef(null)

  const connect = useCallback(() => {
    if (!activeRef.current) return
    if (wsRef.current) wsRef.current.close()

    const wsUrl = url.startsWith('ws') ? url : `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}${url}`
    const ws = new WebSocket(wsUrl)

    ws.onopen = () => setIsConnected(true)
    ws.onmessage = (event) => {
      try {
        setData(JSON.parse(event.data))
      } catch {
        setData(event.data)
      }
    }
    ws.onclose = () => {
      setIsConnected(false)
      if (activeRef.current) {
        reconnectTimeoutRef.current = setTimeout(connect, 3000)
      }
    }
    ws.onerror = () => ws.close()

    wsRef.current = ws
  }, [url])

  useEffect(() => {
    activeRef.current = true
    connect()
    return () => {
      activeRef.current = false
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current)
      if (wsRef.current) wsRef.current.close()
    }
  }, [connect])

  return { data, isConnected }
}
