package main

import (
	"fmt"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"

	"github.com/xyproto/randomstring"
)

//	func BenchmarkHandleWebhook(b *testing.B) {
//		for i := 0; i < b.N; i++ {
//			testing.Main(ha)
//		}
//	}
//
//	func TestMain(m *testing.M) {
//		// call flag.Parse() here if TestMain uses flags
//		os.Exit(m.Run())
//	}
//
//	func BenchmarkHandleWebhook(b *testing.B) {
//		for i := 0; i < b.N; i++ {
//			dp.Handle()
//		}
//	}
func TestHandleWebhook(t *testing.T) {
	file, err := os.Open("./Пример пуша.txt")
	if err != nil {
		return err
	}
	defer file.Close().
    body := &bytes.Buffer{}
	
	rs := randomstring.String(25)
	req := httptest.NewRequest(http.MethodPost, fmt.Sprintf("/webhook/%s", rs), body)
	req.Header.Set("X-Custom-Header", "myvalue")
    req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()
	handleWebhook(w, req)
	res := w.Result()
	defer res.Body.Close()
}
