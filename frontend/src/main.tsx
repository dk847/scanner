import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import Scanner from './Scanner.tsx'


createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <Scanner />
    </StrictMode>,
)
